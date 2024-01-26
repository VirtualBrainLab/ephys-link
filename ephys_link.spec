# -*- mode: python ; coding: utf-8 -*-

from ephys_link import __version__ as version


a = Analysis(
    ['src\\ephys_link\\__main__.py'],
    pathex=[],
    binaries=[('src\\ephys_link\\resources', 'ephys_link\\resources')],
    datas=[],
    hiddenimports=['engineio.async_drivers.aiohttp', 'engineio.async_aiohttp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=f"ephys_link-v{version}-Windows-x86_64",
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
    name='ephys_link',
)
