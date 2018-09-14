import datetime
import os
import winreg


class AnalysisHelper:
    def __init__(self, filepath):
        try:
            f = open(filepath, 'r')
        except:
            raise FileNotFoundError
        self.input_filepath = filepath
        column_lst = ['区县', '主题', '所属小区', '业务受理时间', '结束时间']
        column_i = []
        # Get column index
        for line in f:
            line_lst = line.strip().split(',')
            if len(line_lst) > 1:
                try:
                    column_i = [line_lst.index(column_name) for column_name in column_lst]
                except ValueError:
                    raise ValueError
                break

        self.data = []
        # Get data
        for line in f:
            line_lst = line.strip().split(',')
            self.data.append([line_lst[i] for i in column_i])
        f.close()

    def analyse(self, mode='file', contain_ims=False, contain_business=True):
        data = self.data
        if not contain_ims:
            data = self._screen_ims(data)
        if not contain_business:
            data = self._screen_business(data)
        if mode == 'day':
            result = self._analyse_by_day(data)
        elif mode == 'month':
            result = self._analyse_by_month(data)
        else:   # mode == 'file'
            result = self._analyse_by_file(data)
        output_file_name = self._write_to_csv(result, mode, contain_ims, contain_business)
        return output_file_name

    @staticmethod
    def _screen_business(data):
        return [ele for ele in data if '聚类' not in ele[2]]

    @staticmethod
    def _screen_ims(data):
        return [ele for ele in data if '【IMS】' not in ele[1]]

    def _is_in_time(self, start, end=None):
        if not end:
            return False

        start = self._to_safe_time_format(start)
        end = self._to_safe_time_format(end)
        max_time = start + datetime.timedelta(days=1)
        if start.hour < 12:
            max_time = datetime.datetime(max_time.year, max_time.month, max_time.day, 0, 0, 0)
        else:
            max_time = datetime.datetime(max_time.year, max_time.month, max_time.day, 12, 0, 0)
        if end:
            if end < max_time:
                return True
        else:
            return False

    @staticmethod
    def _to_safe_time_format(dt):
        if type(dt) == str:
            try:
                dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        return dt

    def _analyse_by_file(self, data):
        # Initialize result dict
        counties = ['高区', '环翠区', '经区', '荣成市', '乳山市', '石岛', '文登市']
        result = {}
        for county in counties:
            result[county] = [0, 0]

        for ele in data:
            county = ele[0]
            result[county][0] += 1  # total_num
            if self._is_in_time(ele[3], ele[4]):
                result[county][1] += 1  # in_time_num

            # convert dict to list
        result_lst = [[county, value[0], value[1], str(round(value[1] * 100 / value[0])) + '%']
                      for county, value in result.items()]

        total = ['总计', sum([ele[1] for ele in result_lst]), sum([ele[2] for ele in result_lst])]
        total.append(str(round(total[2] * 100 / total[1])) + '%')
        result_lst.append(total)
        return result_lst

    def _analyse_by_day(self, data):
        days_dic = {}
        for ele in data:
            day = datetime.datetime.strptime(ele[3].split()[0], '%Y-%m-%d')
            if day not in days_dic:
                days_dic[day] = [ele]
            else:
                days_dic[day].append(ele)
        result_dic = {}
        days = list(days_dic.keys())
        for day in sorted(days):
            result_dic[day] = self._analyse_by_file(days_dic[day])
        return result_dic

    def _analyse_by_month(self, data):
        months_dic = {}
        for ele in data:
            start = ele[3]
            month = datetime.datetime.strptime(start.split()[0][:7], '%Y-%m')
            if month not in months_dic:
                months_dic[month] = [ele]
            else:
                months_dic[month].append(ele)
        result_dic = {}
        months = list(months_dic.keys())
        for month in sorted(months):
            result_dic[month] = self._analyse_by_file(months_dic[month])
        return result_dic

    def _write_to_csv(self, data, mode='file', contain_ims=False, contain_business=True):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        desktop_path = str(winreg.QueryValueEx(key, "Desktop")[0])
        new_file_name = '及时率生成结果{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        new_file_path = os.path.join(desktop_path, new_file_name)
        f = open(new_file_path, 'w')
        if mode == 'day':
            self._write_by_day(f, data)
        elif mode == 'month':
            self._write_by_month(f, data)
        elif mode == 'file':
            self._write_by_file(f, data)

        f.write('\n\n')

        # UnicodeEnocodeError raised by filename
        f.write('数据源文件: ')
        for char in self.input_filepath:
            try:
                f.write(char)
            except UnicodeEncodeError:
                f.write('?')
        f.write('\n')

        if contain_ims:
            f.write('未剔除IMS\n')
        else:
            f.write('剔除IMS\n')
        if contain_business:
            f.write('未剔除聚类\n')
        else:
            f.write('剔除聚类\n')

        f.close()
        return new_file_name

    @staticmethod
    def _write_by_day(f, data):
        days = data.keys()
        f.write(',{}\n'.format(',,,'.join([day.strftime('%m/%d') for day in days])))
        f.write('区县' + ',受理量,及时量,及时率' * len(days) + '\n')
        for i in range(len(data[list(days)[0]])):
            count = 0
            for ele in data:
                if not count:
                    county_data = data[ele][i]
                else:
                    county_data = data[ele][i][1:]
                f.write(','.join(map(str, county_data)))
                count += 1
                f.write(',')
            f.write('\n')

    @staticmethod
    def _write_by_month(f, data):
        months = data.keys()
        f.write(',{}\n'.format(',,,'.join([month.strftime('%Y/%m') for month in months])))
        f.write('区县' + ',受理量,及时量,及时率' * len(months) + '\n')
        for i in range(len(data[list(months)[0]])):
            count = 0
            for ele in data:
                if not count:
                    county_data = data[ele][i]
                else:
                    county_data = data[ele][i][1:]
                f.write(','.join(map(str, county_data)))
                count += 1
                f.write(',')
            f.write('\n')

    @staticmethod
    def _write_by_file(f, data):
        f.write('区县,受理量,及时量,及时率\n')
        for ele in data:
            f.write(','.join(map(str, ele)) + '\n')


def main():
    analysis_helper = AnalysisHelper('20180912091237558.csv')
    analysis_helper.analyse(mode='month')


if __name__ == '__main__':
    main()
