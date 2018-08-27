import tkinter
from tkinter import ttk, filedialog, messagebox
from analysis_helper import AnalysisHelper


class AnalysisView:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("及时率生成小工具")
        self.root.resizable(0, 0)

        self.frame = ttk.Frame(self.root)
        self.frame['padding'] = 20

        self.file_label = ttk.Label(self.frame, text='导入文件: ')
        self.file_var = tkinter.StringVar()
        self.file_entry = ttk.Entry(self.frame, width=40, textvariable=self.file_var)
        self.browse_button = ttk.Button(self.frame, text='浏览', width=5, command=self._click_browse)

        self.mode_frame = ttk.Frame(self.frame)
        self.mode_var = tkinter.StringVar()
        self.day_radiobutton = ttk.Radiobutton(self.mode_frame, text='日', value='day', variable=self.mode_var)
        self.month_radiobutton = ttk.Radiobutton(self.mode_frame, text='月', value='month', variable=self.mode_var)
        self.file_radiobutton = ttk.Radiobutton(self.mode_frame, text='文件', value='file', variable=self.mode_var)
        self.mode_var.set('day')

        self.other_options_frame = ttk.Frame(self.frame)
        self.screen_ims_var = tkinter.BooleanVar()
        self.screen_ims_checkbutton = ttk.Checkbutton(self.other_options_frame, text='剔除IMS',
                                                      variable=self.screen_ims_var)
        self.screen_ims_var.set(True)
        self.screen_business_var = tkinter.BooleanVar()
        self.screen_business_checkbutton = ttk.Checkbutton(self.other_options_frame, text='剔除聚类',
                                                           variable=self.screen_business_var)

        self.start_button = ttk.Button(self.frame, text='开始生成', width=8, command=self._click_start)

    def gui_arrang(self):
        self.frame.grid(row=0, column=0)
        self.file_label.grid(row=0, column=0)
        self.file_entry.grid(row=0, column=1, columnspan=3)
        self.browse_button.grid(row=0, column=4)

        self.mode_frame.grid(row=1, column=0)
        self.day_radiobutton.grid(row=0, column=0, sticky='w')
        self.month_radiobutton.grid(row=1, column=0, sticky='w')
        self.file_radiobutton.grid(row=2, column=0, sticky='w')

        self.other_options_frame.grid(row=1, column=1)
        self.screen_ims_checkbutton.grid(row=0, column=0)
        self.screen_business_checkbutton.grid(row=1, column=0)

        self.start_button.grid(row=1, column=3, columnspan=2, sticky='se')

        for child in self.root.winfo_children():
            child.grid_configure(padx=10, pady=10)

    def _click_browse(self):
        path = tkinter.filedialog.askopenfilename(filetypes=[('CSV文件', '*.csv')])
        self.file_var.set(path)

    def _click_start(self):
        try:
            analysis_helper = AnalysisHelper(self.file_var.get())
        except FileNotFoundError:
            messagebox.showerror('错误', '文件不存在')
            return
        except ValueError:
            messagebox.showerror('错误', '文件需包含<区县>, <主题>, <所属小区>, <业务受理时间>, <结束时间>')
            return

        #TODO: mode
        analysis_helper.analyse(mode=self.mode_var,
                                contain_ims=not self.screen_ims_var,
                                contain_business=not self.screen_business_checkbutton)
