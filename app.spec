# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[
        ('/usr/lib/x86_64-linux-gnu/qt6/plugins/platforms/', 'qt6_plugins/platforms'),
        ('/usr/lib/x86_64-linux-gnu/qt6/plugins/xcbglintegrations/', 'qt6_plugins/xcbglintegrations')
	],
    data=[
        ("src/icons/*", "icons"),
        ("src/default_album.png", "."),
        ("mini-player.desktop", "."),
    ],
    hiddenimports=["PyQt6.QtMultimedia", "PyQt6.QtSvg"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.data,
    [],
    name="MiniPlayer",
    debug=False,
    strip=True,
    upx=True,
    bootloader_ignore_signals=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="src/icons/mini-player.ico",
)
