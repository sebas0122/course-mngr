# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SQLModel integration for type-safe database models
- Course model with full SQLModel support
- Professor model with validation
- Comprehensive test suite for SQLModel integration
- SQLModel migration documentation
- SQLModel usage guide with examples
- requirements.txt for easy dependency installation
- .env.example template for configuration

### Changed
- Migrated from dataclasses to SQLModel for Course and Professor
- Updated courses_functions.py to work with SQLModel objects
- Changed retrieveDBTable to return SQLModel objects instead of DataFrames
- Updated getClassesList to work with list of Course objects
- Updated getProfessorsData to work with list of Professor objects
- Modified addProfessorToDB to use model_dump() for serialization
- Updated main.py to use courses_list instead of dataframe
- Improved type safety across the entire application

### Fixed
- Import error in professor.py (removed unused validator import)
- Type validation for all database operations
- Consistency in data handling throughout the application

## [1.0.0] - 2024-10

### Added
- Initial release
- Visual drag-and-drop schedule management
- Course CRUD operations (Create, Read, Update, Delete)
- Professor management
- Excel export functionality
- Supabase database integration
- CustomTkinter GUI
- Multi-semester support (Levels 1-9 and specializations)
- Real-time schedule visualization
- Class and laboratory separation

### Features
- Add and edit courses with detailed information
- Delete courses with confirmation
- Add professors with complete profiles
- Generate Excel reports from database
- Drag-and-drop interface for schedule modifications
- Color-coded courses for visual identification
- Information panels with course/lab details
- Multi-group support

### Database
- Materias (courses) table with full schema
- Profesores (professors) table with profiles
- Cloud-based Supabase integration
- Real-time synchronization

### UI/UX
- Modern interface with CustomTkinter
- Responsive design
- Intuitive controls and buttons
- Visual feedback for user actions
- Full-screen windowed mode

---

## Version History

- **Unreleased** - SQLModel integration and enhanced type safety
- **1.0.0** - Initial release with core functionality

## Migration Notes

### To SQLModel (Unreleased → Current)

If you're upgrading from a pre-SQLModel version:

1. **Install new dependencies**:
   ```bash
   pip install sqlmodel
   ```

2. **Update imports**: If you have custom scripts, update imports:
   ```python
   # Old
   from dataclasses import dataclass
   
   # New
   from sqlmodel import SQLModel, Field
   ```

3. **Update object creation**: 
   ```python
   # Old
   professor = Professor(name="...", id_number=123, email="...")
   
   # New
   professor = Professor(nombre="...", identificacion=123, correo="...")
   ```

4. **API changes**: See [SQLMODEL_MIGRATION.md](SQLMODEL_MIGRATION.md) for complete details

### Database Compatibility

- ✅ No database schema changes required
- ✅ All existing data remains compatible
- ✅ Column names unchanged (Spanish names preserved)
- ✅ Full backward compatibility with existing database

## Future Plans

- [ ] Standalone executable (.exe) for Windows
- [ ] Conflict detection and warnings
- [ ] Automated schedule optimization
- [ ] Multiple user roles and permissions
- [ ] Backup and restore functionality
- [ ] Advanced filtering and search
- [ ] Course analytics and statistics
- [ ] Email notifications for changes
- [ ] Mobile/web version
- [ ] Integration with university systems

## Support

For issues, questions, or feature requests, please visit:
https://github.com/nparra-code/course-mngr/issues
