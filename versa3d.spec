# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hiddenimports = ['vtk',
              'vtkmodules',
              'vtkmodules.all',
              'vtkmodules.qt.QVTKRenderWindowInteractor',
              'vtkmodules.util',
              'vtkmodules.util.numpy_support',
			  'PIL']

a = Analysis(['app.py'],
             pathex=['.'],
             binaries=[],
             datas=[('./designer_files/*.ui','designer_files'),
                    ('./designer_files/icon/*.svg','designer_files/icon'),
                    ('./designer_files/icon/vtk_icon/*.png','designer_files/icon/vtk_icon'),
					('./configs', 'configs')],
             hiddenimports=hiddenimports,
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
          name='versa3d',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='versa3d')
