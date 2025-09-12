# -*- mode: python ; coding: utf-8 -*-

from argparse import ArgumentParser
from importlib import resources

from PyInstaller.utils.hooks import collect_submodules

from ephys_link.__about__ import __version__ as version

parser = ArgumentParser()
parser.add_argument("-d", "--dir", action="store_true", help="Outputs a directory")
options = parser.parse_args()

FILE_NAME = f"EphysLink-v{version}"

# Collect binding modules.
bindings = [binding for binding in collect_submodules("ephys_link.bindings") if binding != "ephys_link.bindings"]

# Collect Sensapex SDK.
ump_sdk_path = str(resources.files('sensapex').joinpath('libum.dll'))

# noinspection PyUnresolvedReferences
a = Analysis(
    ['src\\ephys_link\\__main__.py'],
    pathex=[],
    binaries=[(ump_sdk_path, 'sensapex')],
    datas=[],
    hiddenimports=['engineio.async_drivers.aiohttp'] + bindings,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure)

if options.dir:
    # noinspection PyUnresolvedReferences
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exlude_binaries=True,
        name=FILE_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='docs\\assets\\favicon.ico',
    )
    # noinspection PyUnresolvedReferences
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, upx_exclude=[], name=FILE_NAME)
else:
    # noinspection PyUnresolvedReferences
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name=FILE_NAME,
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
        icon='docs\\assets\\favicon.ico',
    )
