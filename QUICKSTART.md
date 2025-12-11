# Quick Start Guide 🚀

Get up and running with Course Manager in 5 minutes!

## Prerequisites Checklist

Before you begin, ensure you have:
- [ ] Python 3.10 or higher installed
- [ ] pip package manager
- [ ] Internet connection
- [ ] A Supabase account (free tier is fine)

## Step-by-Step Setup

### 1. Clone the Repository (1 minute)

```bash
git clone https://github.com/nparra-code/course-mngr.git
cd course-mngr
```

### 2. Create Virtual Environment (30 seconds)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### 4. Set Up Supabase (2 minutes)

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Click "New Project"
3. Fill in the project details and wait for it to initialize
4. Go to **Project Settings → API**
5. Copy these two values:
   - **Project URL**
   - **anon/public key**

### 5. Configure Environment (30 seconds)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and paste your Supabase credentials:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   ```

### 6. Create Database Tables (1 minute)

1. In Supabase, go to **SQL Editor**
2. Click "New Query"
3. Paste this SQL:

```sql
-- Courses table
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

-- Professors table
CREATE TABLE profesores (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  identificacion INTEGER UNIQUE NOT NULL,
  correo TEXT NOT NULL,
  catedra BOOLEAN DEFAULT FALSE,
  contratacion TEXT DEFAULT 'NO ESPECIFICADO',
  formacion TEXT DEFAULT 'NO ESPECIFICADO'
);

-- Add some sample data (optional)
INSERT INTO profesores (nombre, identificacion, correo, catedra, contratacion, formacion)
VALUES 
  ('Dr. John Doe', 123456, 'john.doe@university.edu', true, 'PLANTA', 'DOCTORADO'),
  ('Prof. Jane Smith', 789012, 'jane.smith@university.edu', false, 'OCASIONAL', 'MAESTRÍA');

INSERT INTO materias (nombre, facultad, dependencia, ide, materia, grupo, tipo, es_lab, nivel, horas_teoricas, horas_practicas, horas_tp, electiva, es_dept, horario, profesor, aula)
VALUES 
  ('INFORMÁTICA I', 2, 2, 'IIE', 1, 1, 'T-P', false, 1, 4, 3, 0, false, true, 'L16-18|M8-10', ARRAY[123456], 'A101');
```

4. Click **Run** (or press Ctrl+Enter)

### 7. Launch the Application (10 seconds)

```bash
python main.py
```

Or on Linux/Mac:
```bash
python3 main.py
```

## 🎉 You're Done!

The application should now open in a full-screen window. You should see:
- A schedule grid with time slots
- Day labels (Lunes, Martes, etc.)
- Theory and Lab sections
- Control buttons on the right side

## First Steps

### Try These Actions:

1. **Select a semester**: Use the dropdown menu and click "Aceptar"
2. **View course details**: Click on any course in the schedule
3. **Add a professor**: Click "Añadir Profesor" button
4. **Add a course**: Click "Añadir Clase" button
5. **Export to Excel**: Click "Exportar a Excel" button

## Common Issues

### "ModuleNotFoundError"
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

### "Connection Error" or "Database Error"
- Check your internet connection
- Verify `.env` file has correct credentials
- Ensure Supabase project is active

### "Permission Denied"
- On Linux/Mac, you might need: `chmod +x main.py`

### Application Won't Start
- Verify Python version: `python --version` (should be 3.10+)
- Check all dependencies installed: `pip list`

## Need Help?

- 📖 Read the [full README](README.md)
- 🔧 Check [SQLMODEL_USAGE.md](SQLMODEL_USAGE.md) for API details
- 🐛 Report bugs on [GitHub Issues](https://github.com/nparra-code/course-mngr/issues)
- 💬 Ask questions in GitHub Discussions

## Next Steps

Once you're comfortable with the basics:

1. Explore all features (Edit, Delete, Drag-and-drop)
2. Add your real course data
3. Customize for your department's needs
4. Check out [SQLMODEL_USAGE.md](SQLMODEL_USAGE.md) for programmatic usage

---

**Time to complete**: ~5 minutes  
**Difficulty**: Beginner-friendly  
**Support**: Available via GitHub Issues

Happy scheduling! 📚✨
