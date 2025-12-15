# -*- mode: python ; coding: utf-8 -*-
##
# @file build_exe.spec
# @brief PyInstaller specification file for Course Manager
#
# This file configures how PyInstaller builds the executable.
# Customize the settings below to change the app name, icon, and other options.

# ===== CONFIGURATION OPTIONS =====
# Change these values to customize your executable:

APP_NAME = 'CourseManager'              # Name of the executable (without .exe)
APP_VERSION = '1.0.0'                   # Application version
APP_DESCRIPTION = 'Course Schedule Manager'  # Description
COMPANY_NAME = 'Universidad de Antioquia'    # Company/Organization name
COPYRIGHT = 'Copyright (c) 2025'        # Copyright notice
ICON_FILE = 'icon.ico'                  # Icon file (place .ico file in project root)

# Advanced options:
ONE_FILE = True                         # True = single .exe, False = folder with dependencies
CONSOLE = False                         # True = show console, False = hide console (GUI app)
DEBUG = False                           # True = enable debug output

# ===== END CONFIGURATION =====

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect hidden imports
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'customtkinter',
    'PIL',
    'PIL._tkinter_finder',
    'sqlmodel',
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.orm',
    'sqlalchemy.sql',
    'sqlalchemy.sql.default_comparator',
    'pydantic',
    'pydantic.fields',
    'pydantic_core',
    'supabase',
    'postgrest',
    'httpx',
    'pandas',
    'openpyxl',
    'dotenv',
    'python-dotenv',
]

# Collect data files for customtkinter and other packages
datas = []
try:
    datas += collect_data_files('customtkinter')
except:
    pass

try:
    datas += collect_data_files('sqlmodel')
except:
    pass

try:
    datas += collect_data_files('pydantic')
except:
    pass

# Add .env file if it exists
if os.path.exists('.env'):
    datas.append(('.env', '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.random._examples',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if ONE_FILE:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=APP_NAME,
        debug=DEBUG,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=CONSOLE,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON_FILE if os.path.exists(ICON_FILE) else None,
        version='version_info.txt' if os.path.exists('version_info.txt') else None,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=DEBUG,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=CONSOLE,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON_FILE if os.path.exists(ICON_FILE) else None,
        version='version_info.txt' if os.path.exists('version_info.txt') else None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=APP_NAME,
    )
