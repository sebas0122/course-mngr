# Building Executable (.exe) - Complete Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install PyInstaller

```powershell
pip install pyinstaller
```

### Step 2: Build the Executable

**Via Command Line:**
```powershell
pyinstaller build_exe.spec --clean --noconfirm
```

### Step 3: Find Your Executable

Your `.exe` will be in: `dist/CourseManager.exe`

---

## ⚙️ Customization Options

### 1. Change App Name

Edit `build_exe.spec`, line 12:
```python
APP_NAME = 'CourseManager'  # Change to your desired name
```

### 2. Change App Icon

1. **Get an icon file (.ico format)**
   - Use an online converter: https://convertio.co/png-ico/
   - Or use an icon editor
   - Icon should be 256x256 pixels or larger

2. **Save as `icon.ico` in project root**, or:

3. **Edit `build_exe.spec`, line 16:**
   ```python
   ICON_FILE = 'your_icon.ico'  # Point to your icon file
   ```

### 3. Change App Description & Company

Edit `build_exe.spec`:
```python
APP_VERSION = '1.0.0'                      # Line 13
APP_DESCRIPTION = 'Course Schedule Manager' # Line 14
COMPANY_NAME = 'Universidad de Antioquia'  # Line 15
COPYRIGHT = 'Copyright (c) 2025'           # Line 16
```

Edit `version_info.txt`:
```python
StringStruct(u'CompanyName', u'Your Company'),
StringStruct(u'FileDescription', u'Your Description'),
StringStruct(u'LegalCopyright', u'Copyright (c) 2025 Your Name'),
StringStruct(u'ProductName', u'Your Product Name'),
```

### 4. One File vs Folder

**One File** (default) - Single .exe:
```python
ONE_FILE = True  # Line 19 in build_exe.spec
```

**Folder** - .exe with DLLs folder:
```python
ONE_FILE = False
```

### 5. Show/Hide Console Window

**Hide Console** (default for GUI apps):
```python
CONSOLE = False  # Line 20 in build_exe.spec
```

**Show Console** (for debugging):
```python
CONSOLE = True
```

---

## 📁 Files Created

- **`build_exe.spec`** - PyInstaller configuration (customize here!)
- **`version_info.txt`** - Windows version information
- **`build_exe.bat`** - One-click build script

---

## 🔧 Advanced Options

### Include Additional Files

Edit `build_exe.spec`, in the `datas` section:
```python
datas = [
    ('.env', '.'),           # Include .env file
    ('data', 'data'),        # Include data folder
    ('images', 'images'),    # Include images folder
]
```

### Exclude Unnecessary Modules

Edit `build_exe.spec`, in the `excludes` section:
```python
excludes=[
    'matplotlib',
    'numpy.random._examples',
    'test',
    'unittest',
],
```

### Change Output Directory

By default outputs to `dist/`, change in terminal:
```powershell
pyinstaller build_exe.spec --distpath=output --clean
```

---

## 📦 Distribution

### Single File Mode (ONE_FILE = True)

Your app is ready to distribute:
- **File:** `dist/CourseManager.exe`
- **Size:** ~50-100 MB (includes Python + all dependencies)
- **Distribution:** Just copy this one file

### Folder Mode (ONE_FILE = False)

Your app folder structure:
```
dist/
└── CourseManager/
    ├── CourseManager.exe  # Main executable
    ├── *.dll              # Required libraries
    └── _internal/         # Internal files
```

**To distribute:** Zip the entire `CourseManager` folder

---

## 🎯 Important Notes

### .env File

Your `.env` file with database credentials **will be included** in the executable. 

**Security Options:**

1. **Remove .env from build:**
   Comment out in `build_exe.spec`:
   ```python
   # if os.path.exists('.env'):
   #     datas.append(('.env', '.'))
   ```

2. **Store .env separately:**
   - Build without .env
   - Place .env next to .exe when distributing
   - App will read it from the same folder

3. **Use environment variables:**
   - Set credentials as Windows environment variables
   - App reads from system environment

### Database Connection

The app connects to Supabase (remote database), so:
- ✅ No local database files needed
- ✅ Works on any computer with internet
- ⚠️ Requires valid .env credentials

---

## 🐛 Troubleshooting

### "Failed to execute script"

**Solution 1:** Build with console enabled to see errors:
```python
CONSOLE = True  # in build_exe.spec
```

**Solution 2:** Check all dependencies installed:
```powershell
pip install -r requirements.txt
```

### "Module not found" errors

Add missing modules to `hiddenimports` in `build_exe.spec`:
```python
hiddenimports = [
    'tkinter',
    'customtkinter',
    'missing_module_name',  # Add here
]
```

### Icon not showing

1. Verify `icon.ico` exists in project root
2. Icon must be valid .ico format (not just renamed .png)
3. Check `ICON_FILE` path in `build_exe.spec`

### Large file size

Normal! Python executables are 50-100+ MB because they include:
- Python interpreter
- All libraries (tkinter, customtkinter, pandas, etc.)
- Dependencies

**To reduce size:**
- Use folder mode (`ONE_FILE = False`)
- Exclude unused modules
- Use UPX compression (enabled by default)

### Antivirus warnings

Some antivirus software flags PyInstaller executables as suspicious:
- This is a false positive
- Sign your executable with a code signing certificate
- Or whitelist in antivirus

---

## 🔄 Rebuild After Changes

After modifying your Python code:

1. Run `build_exe.bat` again, or:
2. Run: `pyinstaller build_exe.spec --clean --noconfirm`

The `--clean` flag ensures old builds are removed.

---

## 📋 Build Options Reference

### In `build_exe.spec`:

| Option | Values | Description |
|--------|--------|-------------|
| `APP_NAME` | String | Executable name (without .exe) |
| `APP_VERSION` | String | Version number |
| `APP_DESCRIPTION` | String | App description |
| `COMPANY_NAME` | String | Company/Organization |
| `COPYRIGHT` | String | Copyright notice |
| `ICON_FILE` | Path | Icon file path (.ico) |
| `ONE_FILE` | True/False | Single file vs folder |
| `CONSOLE` | True/False | Show console window |
| `DEBUG` | True/False | Enable debug output |

### Command Line Options:

```powershell
# Clean build
pyinstaller build_exe.spec --clean

# Don't ask for confirmation
pyinstaller build_exe.spec --noconfirm

# Custom output directory
pyinstaller build_exe.spec --distpath=output

# Combined
pyinstaller build_exe.spec --clean --noconfirm --distpath=my_builds
```

---

## 🎨 Creating an Icon

### From Image to .ico:

1. **Start with PNG/JPG** (256x256 or larger)
2. **Convert online:**
   - https://convertio.co/png-ico/
   - https://www.icoconverter.com/
   - https://favicon.io/favicon-converter/

3. **Or use GIMP:**
   - Open image in GIMP
   - Image → Scale Image → 256x256
   - File → Export As → filename.ico

4. **Save as `icon.ico`** in project root

### Icon Requirements:
- ✅ Format: .ico (not .png renamed)
- ✅ Size: 256x256 recommended (supports 16x16 to 256x256)
- ✅ Color: Full color supported
- ✅ Transparency: Supported

---

## 📦 Recommended Build Settings

### For Distribution:
```python
APP_NAME = 'CourseManager'
ONE_FILE = True      # Single file for easy distribution
CONSOLE = False      # Hide console for professional look
DEBUG = False        # Disable debug messages
```

### For Development/Testing:
```python
APP_NAME = 'CourseManager_Dev'
ONE_FILE = False     # Faster builds
CONSOLE = True       # See error messages
DEBUG = True         # Enable debug output
```

---

## 🆘 Need Help?

- PyInstaller docs: https://pyinstaller.org/en/stable/
- Icon converters: https://convertio.co/png-ico/
- Code signing: https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools

---

## ✅ Checklist

Before building:
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] PyInstaller installed: `pip install pyinstaller`
- [ ] Icon file created (optional): `icon.ico`
- [ ] Customized `build_exe.spec` settings
- [ ] Tested app runs: `python main.py`

After building:
- [ ] Executable created in `dist/`
- [ ] Test executable runs without errors
- [ ] Icon displays correctly
- [ ] App name is correct
- [ ] Database connection works
- [ ] All features work as expected
