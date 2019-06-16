# -*- mode: python -*-

block_cipher = None


a = Analysis(['stpdf_cli.py'],
             pathex=['D:\\Git\\ScanToPDF\\src'],
             binaries=[],
             datas=[("version.pckl", ".")],
             hiddenimports=[],
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
          name='STPDF-cli',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               Tree('locale/', prefix='locale/'),
               a.datas,
               strip=False,
               upx=True,
               name='stpdf_cli')
