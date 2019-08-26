# -*- mode: python -*-

block_cipher = None


a = Analysis(['gui.py'],
             pathex=[],
             binaries=[("version.pckl", ".")],
             datas=[],
             hiddenimports=["PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.sip", "PyQt5.QtWidgets"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='STPDF-gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               Tree('locale/', prefix='locale/'),
               Tree('themes/', prefix='themes/'),
               Tree('docs/', prefix='docs/'),
               a.datas,
               strip=False,
               upx=True,
               name='STPDF')
