# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['G:\\PyCharmProjects\\及时率分析', 'G:\\PyCharmProjects\\及时率分析\\venv', 'G:\\PyCharmProjects\\及时率分析', 'G:\\PyCharmProjects\\及时率分析\\venv\\Lib\\site-packages'],
             binaries=[],
             datas=[('panda_128px_1202518_easyicon.net.ico', '\\')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='IntimeP',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, icon='panda_128px_1202518_easyicon.net.ico' )
