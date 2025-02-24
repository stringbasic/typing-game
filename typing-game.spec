# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['code.py'],
             pathex=[],
             binaries=[],
             datas=[('words.txt', '.')],  # Include words.txt in the same directory
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
          name='TypingGame',  # Name of the executable
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )  # Set console=False for a windowed application
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='typinggame') #Name of the folder created
