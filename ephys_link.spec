# -*- mode: python ; coding: utf-8 -*-

from ephys_link.__about__ import __version__ as version

a = Analysis(
    ['src\\ephys_link\\__main__.py'],
    pathex=[],
    binaries=[('src\\ephys_link\\resources', 'ephys_link\\resources')],
    datas=[],
    hiddenimports=['engineio.async_drivers.aiohttp'],
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
    a.binaries,
    a.datas,
    [],
    name=f"EphysLink-v{version}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\\icon.ico',
)
