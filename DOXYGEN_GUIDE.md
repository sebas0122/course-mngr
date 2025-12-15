# Doxygen Documentation Guide

## Step 1: Install Doxygen

### Windows Installation

**Option A: Using Chocolatey (Recommended)**
```powershell
choco install doxygen.install
```

**Option B: Manual Installation**
1. Download Doxygen from: https://www.doxygen.nl/download.html
2. Run the installer (doxygen-x.x.x-setup.exe)
3. Follow the installation wizard
4. Add Doxygen to your PATH if not done automatically

**Option C: Using winget**
```powershell
winget install DimitriVanHeesch.Doxygen
```

### Verify Installation
```powershell
doxygen --version
```

## Step 2: Optional - Install Graphviz (for diagrams)

Graphviz enables Doxygen to generate class diagrams and dependency graphs.

**Using Chocolatey:**
```powershell
choco install graphviz
```

**Manual Download:**
- Download from: https://graphviz.org/download/
- Install and add to PATH

**Update Doxyfile if you install Graphviz:**
- Open `Doxyfile`
- Change `HAVE_DOT = NO` to `HAVE_DOT = YES`

## Step 3: Generate Documentation

### Generate HTML Documentation

Navigate to the project root directory and run:

```powershell
cd C:\Users\nelso\course-mngr
doxygen Doxyfile
```

This will create documentation in `docs/doxygen/html/`

### View the Documentation

Open the generated HTML documentation:

```powershell
# Open in default browser
start docs/doxygen/html/index.html
```

Or navigate to: `C:\Users\nelso\course-mngr\docs\doxygen\html\index.html`

## Step 4: Generate PDF Documentation (Optional)

If you want PDF documentation, you need to install LaTeX:

### Install MiKTeX (LaTeX for Windows)

**Using Chocolatey:**
```powershell
choco install miktex
```

**Manual:**
- Download from: https://miktex.org/download
- Install with default options

### Generate PDF

```powershell
# Generate documentation with LaTeX enabled
doxygen Doxyfile

# Navigate to LaTeX output directory
cd docs/doxygen/latex

# Compile the LaTeX to PDF
pdflatex refman.tex
makeindex refman.idx
pdflatex refman.tex
```

The final PDF will be: `docs/doxygen/latex/refman.pdf`

## Documentation Structure

After generation, you'll find:

```
docs/
└── doxygen/
    ├── html/           # HTML documentation
    │   ├── index.html  # Main page (start here)
    │   ├── files.html  # File list
    │   ├── classes.html # Class list
    │   └── ...
    └── latex/          # LaTeX/PDF documentation
        └── refman.tex  # LaTeX source
```

## Customizing the Documentation

### Edit Project Information

Edit `Doxyfile` and modify:
- `PROJECT_NAME` - Your project name
- `PROJECT_NUMBER` - Version number
- `PROJECT_BRIEF` - Short description
- `PROJECT_LOGO` - Path to logo image (optional)

### Change Output Directory

Edit `Doxyfile`:
```
OUTPUT_DIRECTORY = ./docs/doxygen
```

### Include/Exclude Files

Edit `Doxyfile`:
```
INPUT = . docs
EXCLUDE = __pycache__ build .git venv
FILE_PATTERNS = *.py *.md
```

## What's Already Documented

All Python files in your project now have Doxygen-compatible comments:

- ✅ **main.py** - GUI application with all functions documented
- ✅ **course.py** - Course data model
- ✅ **professor.py** - Professor data model  
- ✅ **courses_functions.py** - Database and utility functions
- ✅ **dnd.py** - Drag-and-drop functionality
- ✅ **excel_analysis.py** - Excel import/export
- ✅ **sql_to_python.py** - Database queries
- ✅ **test_sqlmodel_integration.py** - Test suite

## Documentation Features

The generated documentation includes:

- **File Documentation** - Description of each Python file
- **Class Documentation** - All classes with attributes and methods
- **Function Documentation** - Parameters, return values, and descriptions
- **Cross-References** - Links between related code
- **Source Browser** - View source code with syntax highlighting
- **Search Functionality** - Search through all documentation
- **Class Diagrams** - Visual representation of relationships (if Graphviz installed)

## Updating Documentation

After making code changes:

1. Update the Doxygen comments in your Python files
2. Re-run: `doxygen Doxyfile`
3. Documentation will be regenerated automatically

## Troubleshooting

### "doxygen is not recognized"
- Ensure Doxygen is installed
- Add Doxygen to your PATH environment variable
- Restart your terminal/PowerShell

### Empty or missing pages
- Check that FILE_PATTERNS includes `*.py`
- Verify INPUT paths are correct
- Ensure Python files have proper Doxygen comments

### Warnings during generation
- Review the terminal output for specific issues
- Most warnings are informational and safe to ignore
- Critical errors will prevent generation

## Quick Reference - Doxygen Comment Syntax

```python
##
# @file filename.py
# @brief Brief description
#
# Detailed description
#
# @author Author Name
# @date Date

##
# @brief Function brief description
#
# Detailed description
#
# @param param1 Description of parameter 1
# @param param2 Description of parameter 2
# @return Description of return value
def my_function(param1, param2):
    pass

##
# @class ClassName
# @brief Class brief description
#
# Detailed description
class ClassName:
    pass
```

## Need Help?

- Doxygen Manual: https://www.doxygen.nl/manual/
- Python + Doxygen: https://www.doxygen.nl/manual/docblocks.html
- Example Projects: https://www.doxygen.nl/examples.html
