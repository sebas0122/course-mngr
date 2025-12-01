# Course Manager

## Overview

**course-mngr** is a centralized application designed for the Electronic and Telecommunications Engineering Department at the University of Antioquia. This project aims to streamline the management of course classrooms and schedules for department chiefs and administrators, replacing the outdated method of handling schedules through multiple files.

### Problem Statement

As of October 2024, the management of schedules has relied on numerous separate files, each requiring manual updates whenever changes are made. This approach is inefficient and prone to errors, making it essential to implement a centralized system. The new application will include a global database, allowing all relevant files to access and update information from a single source, thus enhancing efficiency and accuracy.

## Features

The following features are implemented in this app:

- **UI/UX Design**: A user-friendly interface to enhance user experience for administrators and chiefs.
- **Database**: A centralized storage online solution in an SQL format.
- **Interconnection Protocols**: Mechanisms to enable communication between the files and the remote database, ensuring seamless updates and data integrity.
- **Add and Edit Classes**: One can add or edit classes. Add function allows to insert multiple cells that shares name and code in a single request.
- **Delete Classes**: Class deletion is available.
- **Add Professor**: Now new professors can be added from the interface.
- **Excel Generation**: From the remote databse, an Excel file can be generated with the updated information as it was intended.

## Benefits

- **Centralized Management**: A single source of truth for course schedules and classroom management.
- **Efficiency**: Reduce the time and effort required for manual updates across multiple files.
- **Error Reduction**: Minimize the potential for inconsistencies and errors in scheduling information.

## Getting Started

To get started with the course-mngr project, please refer to the following sections in this README:

1. **Installation**: Instructions on how to set up the application locally.
2. **Usage**: Guidelines on how to use the application once it's up and running.
3. **Contributing**: Information on how to contribute to the project.
4. **License**: Details about the licensing of the project.

## Installation

There are two ways to install and run the **course-mngr** application:

### Option 1: Standalone Executable (Coming Soon)

The easiest way to use the application is to download the pre-built executable file:

1. Download the latest `.exe` file from the releases page.
2. Run the executable file directly on your Windows machine.
3. No additional installation or configuration required.

*Note: The standalone executable is currently under development and will be available soon.*

### Option 2: From Source (Repository)

To run the application from source code:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/course-mngr.git
   cd course-mngr
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install pandas sqlalchemy customtkinter python-dotenv supabase
   ```

5. **Configure environment variables**:
   - Create a `.env` file in the project root directory
   - Add your database credentials and configuration settings

6. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

*Coming soon!*

## License

*Coming soon!*

## Contact

For questions or feedback regarding the course-mngr project, please reach out to --.
