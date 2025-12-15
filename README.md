# Course Manager 📚

<div align="center">

**A modern course schedule management system for academic departments**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![SQLModel](https://img.shields.io/badge/SQLModel-Latest-green.svg)](https://sqlmodel.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 📋 Overview

**course-mngr** is a comprehensive desktop application designed for the Electronic and Telecommunications Engineering Department at the University of Antioquia. This project streamlines the management of course classrooms and schedules for department chiefs and administrators, replacing the outdated method of handling schedules through multiple disconnected files.

### 🎯 Problem Statement

Previously, schedule management relied on numerous separate files, each requiring manual updates whenever changes occurred. This approach was:
- Inefficient and time-consuming
- Prone to inconsistencies and errors
- Difficult to maintain and coordinate
- Lacked a centralized source of truth

**course-mngr** solves these problems with a centralized system backed by a cloud database, ensuring all data is synchronized and accessible from a single, intuitive interface.

## ✨ Features

### Core Functionality

- **📅 Visual Schedule Management**
  - Drag-and-drop interface for easy schedule modifications
  - Real-time visual representation of course timetables
  - Support for multiple semester levels (1-9) and specializations
  - Separate views for theory classes and laboratory sessions

- **🎓 Course Management**
  - Add new courses with detailed information
  - Edit existing course schedules, rooms, and assignments
  - Delete courses with confirmation
  - Multi-group support (automatically combines groups sharing the same schedule)
  - Real-time validation and conflict detection

- **👨‍🏫 Professor Management**
  - Add new professors with complete profiles
  - Track professor information (ID, email, hiring type, education level)
  - Assign multiple professors to a single course
  - View professor assignments across all courses

- **💾 Database Integration**
  - Cloud-based Supabase database for centralized storage
  - Real-time synchronization across all operations
  - Automatic backup and version control
  - Secure authentication and access control

- **📊 Excel Export**
  - Generate comprehensive Excel reports
  - Export schedules by semester or department
  - Formatted output matching institutional requirements
  - Includes all course details, professors, and room assignments

- **🎨 Modern UI/UX**
  - Clean, intuitive interface built with CustomTkinter
  - Responsive design that adapts to screen size
  - Color-coded courses for easy visual identification
  - Information panels with detailed course/lab data

### Technical Features

- **🔧 SQLModel Integration**
  - Type-safe database models with automatic validation
  - Pydantic-powered data validation
  - SQLAlchemy ORM for robust database operations
  - Full type hints and IDE support

- **🔄 Dynamic Schedule System**
  - Flexible schedule format (e.g., "L16-18|M8-10")
  - Support for multiple time slots per course
  - Automatic duration calculation
  - Weekend and evening class support

## 🎁 Benefits

- **Centralized Management**: Single source of truth for all scheduling data
- **Increased Efficiency**: Reduce manual updates from hours to minutes
- **Error Reduction**: Automatic validation prevents scheduling conflicts
- **Real-time Updates**: Changes are immediately reflected across the system
- **Multi-user Support**: Multiple administrators can work simultaneously
- **Scalability**: Easily handles growing course catalogs and complex schedules
- **Data Security**: Cloud backup ensures data is never lost
- **Accessibility**: Access from any computer with internet connection

## 🖼️ Screenshots

### Main Schedule View
![Main Interface](docs/images/main-interface.png)
*Drag-and-drop schedule management with visual time slots*

### Course Information Panel
![Course Details](docs/images/course-info.png)
*Detailed course information with professor assignments*

### Add/Edit Course Dialog
![Add Course](docs/images/add-course.png)
*Intuitive form for adding or editing courses*

## 🏗️ Architecture

The application follows a modular architecture:

```
course-mngr/
├── main.py              # Main application and UI
├── course.py            # Course SQLModel definition
├── professor.py         # Professor SQLModel definition
├── courses_functions.py # Database operations and business logic
├── dnd.py              # Drag-and-drop functionality
├── excel_analysis.py   # Excel export functionality
└── data/               # Data files and templates
```

### Technology Stack

- **Frontend**: CustomTkinter (modern tkinter wrapper)
- **Backend**: Python 3.10+
- **Database**: Supabase (PostgreSQL)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Data Processing**: Pandas
- **Environment**: python-dotenv

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Internet connection (for database access)
- Supabase account with a configured database

### Quick Start

#### Option 1: Standalone Executable (Recommended for End Users)

*Coming soon!* A pre-built executable will be available for easy installation without Python.

#### Option 2: From Source (For Developers)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nparra-code/course-mngr.git
   cd course-mngr
   ```

2. **Create and activate a virtual environment**:
   
   **On Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **On Linux/Mac:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install sqlmodel pandas customtkinter python-dotenv supabase openpyxl
   ```

4. **Configure environment variables**:
   
   Create a `.env` file in the project root directory:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```
   
   **Getting Supabase credentials:**
   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project
   - Go to Project Settings → API
   - Copy the Project URL and anon/public key

5. **Set up the database**:
   
   Run the SQL schema in your Supabase SQL editor:
   ```sql
   -- Create materias table
   CREATE TABLE materias (
     id SERIAL PRIMARY KEY,
     nombre TEXT NOT NULL,
     facultad INTEGER NOT NULL,
     dependencia INTEGER NOT NULL,
     ide TEXT NOT NULL,
     materia INTEGER NOT NULL,
     grupo INTEGER NOT NULL,
     tipo TEXT NOT NULL,
     es_lab BOOLEAN NOT NULL,
     nivel INTEGER NOT NULL,
     horas_teoricas INTEGER NOT NULL,
     horas_practicas INTEGER NOT NULL,
     horas_tp INTEGER NOT NULL,
     electiva BOOLEAN NOT NULL,
     es_dept BOOLEAN NOT NULL,
     horario TEXT NOT NULL,
     profesor INTEGER[] NOT NULL,
     aula TEXT NOT NULL
   );

   -- Create profesores table
   CREATE TABLE profesores (
     id SERIAL PRIMARY KEY,
     nombre TEXT NOT NULL,
     identificacion INTEGER UNIQUE NOT NULL,
     correo TEXT NOT NULL,
     catedra BOOLEAN DEFAULT FALSE,
     contratacion TEXT DEFAULT 'NO ESPECIFICADO',
     formacion TEXT DEFAULT 'NO ESPECIFICADO'
   );
   ```

6. **Run the application**:
   ```bash
   python main.py
   ```
   
   Or on Linux/Mac:
   ```bash
   python3 main.py
   ```

### Verification

To verify your installation, run the test suite:
```bash
python3 test_sqlmodel_integration.py
```

You should see all tests passing with ✓ marks.

## 📖 Usage

### Basic Workflow

1. **Launch the Application**
   ```bash
   python main.py
   ```

2. **Select Semester Level**
   - Use the dropdown menu on the right side
   - Choose from Nivel 1-9 or specializations (E. Control, E. Digitales, etc.)
   - Click "Aceptar" to load the schedule

3. **View Schedule**
   - Theory classes appear on the left grid
   - Laboratory sessions appear on the right grid
   - Click any class to see detailed information in the bottom panel

### Managing Courses

#### Adding a New Course

1. Click the **"Añadir Clase"** button
2. Fill in the course details:
   - Course code or search by name
   - Group number
   - Schedule (format: "L16-18|M8-10")
   - Room/classroom
   - Professor IDs (comma-separated)
   - Course type (Theory/Lab)
   - Semester level
3. Click "Save" to add to the database

#### Editing a Course

1. Click on the course in the schedule
2. Click the **"Editar Clase"** button
3. Modify the desired fields
4. The changes are highlighted but not saved yet
5. Click **"Guardar Cambios"** to save to the database

#### Deleting a Course

1. Click on the course to select it
2. Click the **"Eliminar Clase"** button
3. Confirm the deletion
4. Click **"Guardar Cambios"** to permanently delete

#### Drag and Drop

- Click and drag any course to move it to a different time slot
- The course will snap to the nearest valid position
- Visual feedback shows where the course will be placed
- Changes are tracked and highlighted
- Remember to click **"Guardar Cambios"** to save

### Managing Professors

#### Adding a New Professor

1. Click the **"Añadir Profesor"** button
2. Fill in the professor details:
   - Full name
   - ID number (cédula)
   - Email address
   - Cathedra status (Yes/No)
   - Hiring type (Ocasional, Planta, Cátedra, etc.)
   - Education level (Pregrado, Maestría, Doctorado, etc.)
3. Click "Save" to add to the database

### Exporting to Excel

1. Click the **"Exportar a Excel"** button
2. Choose the destination folder and filename
3. The Excel file will be generated with:
   - All courses for the selected semester
   - Complete professor information
   - Room assignments
   - Schedule details

### Saving Changes

**Important**: Changes are not automatically saved to the database!

- After editing, deleting, or moving courses, click **"Guardar Cambios"**
- A confirmation message will appear when changes are saved
- You can make multiple edits before saving (batch operation)

### Schedule Format

When entering schedules manually, use this format:

- **Single day, single slot**: `L16-18` (Monday 16:00-18:00)
- **Multiple slots**: `L16-18|M8-10` (Monday 16-18 AND Tuesday 8-10)
- **Same time, multiple days**: `LM16-18` (Monday AND Tuesday 16-18)

**Day codes**:
- L = Lunes (Monday)
- M = Martes (Tuesday)
- W = Miércoles (Wednesday)
- J = Jueves (Thursday)
- V = Viernes (Friday)
- S = Sábado (Saturday)

### Keyboard Shortcuts

- `Escape` - Exit fullscreen mode
- Click and drag - Move courses
- Click - Select and view details

## 🔧 Advanced Usage

### Using SQLModel Classes Programmatically

For developers who want to extend or integrate with the application:

```python
from course import Course
from professor import Professor
from courses_functions import connectSQL, retrieveDBTable

# Connect to database
supabase = connectSQL()

# Get all courses
courses = retrieveDBTable(supabase, "materias")

# Filter courses
level_1_courses = [c for c in courses if c.nivel == 1]

# Create a new course
new_course = Course(
    nombre="CIRCUITS I",
    facultad=2,
    dependencia=2,
    ide="IIE",
    materia=5,
    grupo=1,
    tipo="T-P",
    es_lab=False,
    nivel=2,
    horas_teoricas=4,
    horas_practicas=2,
    horas_tp=0,
    electiva=False,
    es_dept=True,
    horario="L10-12|W10-12",
    profesor=[123456],
    aula="B301"
)
```

See [SQLMODEL_USAGE.md](SQLMODEL_USAGE.md) for complete API documentation.

## 📚 Documentation

### For Users
- **[Building Executable](BUILD_INSTRUCTIONS.md)** - Complete guide to create standalone .exe application
- **[Icon Setup](ICON_SETUP.md)** - Instructions for customizing application icon

### For Developers
- **[Doxygen Documentation Guide](DOXYGEN_GUIDE.md)** - Generate code documentation
- **[SQLModel Migration Guide](SQLMODEL_MIGRATION.md)** - Details about the SQLModel architecture
- **[SQLModel Usage Guide](SQLMODEL_USAGE.md)** - API reference and code examples

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Update tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

### Running Tests

```bash
python3 test_sqlmodel_integration.py
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'sqlmodel'`
- **Solution**: Run `pip install sqlmodel` in your virtual environment

**Issue**: Database connection fails
- **Solution**: Check your `.env` file has correct Supabase credentials
- Verify your internet connection
- Ensure your Supabase project is active

**Issue**: Application window doesn't display correctly
- **Solution**: Update CustomTkinter: `pip install --upgrade customtkinter`
- Check your screen resolution settings

**Issue**: Drag and drop not working smoothly
- **Solution**: This is a known limitation with tkinter on some systems
- Try using the Edit button instead

### Getting Help

- Check the [Issues](https://github.com/nparra-code/course-mngr/issues) page
- Read the documentation in the `docs/` folder
- Review [SQLMODEL_USAGE.md](SQLMODEL_USAGE.md) for API questions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Nelson Parra** - *Initial work* - [@nparra-code](https://github.com/nparra-code)

## Acknowledgments

- University of Antioquia - Electronic and Telecommunications Engineering Department
- SQLModel framework by Sebastián Ramírez
- CustomTkinter library by Tom Schimansky
- Supabase for the database infrastructure

## Contact

For questions, feedback, or support regarding the course-mngr project:

- GitHub Issues: [course-mngr/issues](https://github.com/nparra-code/course-mngr/issues)
- Email: Contact through GitHub profile

---

<div align="center">

[Report Bug](https://github.com/nparra-code/course-mngr/issues) · [Request Feature](https://github.com/nparra-code/course-mngr/issues) · [Documentation](docs/)

</div>
