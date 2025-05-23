# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# Collecting all necessary MediaPipe data files (like .tflite)
mediapipe_data = collect_data_files('mediapipe', include_py_files=False)

a = Analysis(
    ['eyevox_app.py'],
    pathex=[],
    binaries=[],
    datas=[('credentials', 'credentials')] + mediapipe_data,
    hiddenimports=[
        'mediapipe.python._framework_bindings.default',
        'tensorflow',
        'sounddevice',
        'wavio'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='eyevox_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='eyevox_app',
)
