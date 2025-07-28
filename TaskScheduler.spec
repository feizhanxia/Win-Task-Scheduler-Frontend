# PyInstaller spec file for Streamlit Task Scheduler Application

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Get the directory of this spec file
spec_root = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(spec_root)],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('xml_builder.py', '.'),
        ('scheduler_cli.py', '.'),
        ('preview.py', '.'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner_utils.script_run_context',
        'streamlit.web.server.server',
        'streamlit.web.server.server_util',
        'streamlit.components.v1',
        'streamlit.elements',
        'streamlit.proto',
        'streamlit.logger',
        'streamlit.config',
        'streamlit.runtime',
        'streamlit.runtime.state',
        'streamlit.runtime.caching',
        'streamlit.runtime.legacy_caching',
        'streamlit.web.bootstrap',
        'altair',
        'jinja2',
        'croniter',
        'tornado',
        'watchdog',
        'validators',
        'pympler',
        'click',
        'toml',
        'tzlocal',
        'pytz',
        'packaging',
        'importlib_metadata',
    ],
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
    a.datas,
    [],
    name='TaskScheduler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
