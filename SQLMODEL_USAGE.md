# SQLModel Usage Guide

## Creating Objects

### Course

```python
from course import Course

# Create a new course
course = Course(
    nombre="INFORMÁTICA I",
    facultad=2,
    dependencia=2,
    ide="IIE",
    materia=1,
    grupo=1,
    tipo="T-P",
    es_lab=False,
    nivel=1,
    horas_teoricas=4,
    horas_practicas=3,
    horas_tp=0,
    electiva=False,
    es_dept=True,
    horario="L16-18|M8-10",  # Schedule format: Day + StartHour-EndHour | ...
    profesor=[123456, 789012],  # List of professor IDs
    aula="A101"
)

# Get the course code
code = course.get_codigo()  # Returns "221"

# Access properties
print(course.nombre)     # "INFORMÁTICA I"
print(course.nivel)      # 1
print(course.horario)    # "L16-18|M8-10"
```

### Professor

```python
from professor import Professor

# Create a new professor
prof = Professor(
    nombre="Dr. John Doe",
    identificacion=123456,
    correo="johndoe@example.com",
    catedra=True,
    contratacion="OCASIONAL",  # Valid: NO ESPECIFICADO, OCASIONAL, PLANTA, CÁTEDRA, CÁTEDRA CALENDARIO
    formacion="DOCTORADO"      # Valid: NO ESPECIFICADO, PREGRADO, MAESTRÍA, DOCTORADO, ESPECIALIZACIÓN
)

# Access properties
print(prof.nombre)          # "Dr. John Doe"
print(prof.identificacion)  # 123456
print(prof.contratacion)    # "OCASIONAL"
```

## Working with the Database

### Retrieving Data

```python
from courses_functions import connectSQL, retrieveDBTable

# Connect to the database
supabase = connectSQL()

# Get all courses as a list of Course objects
courses = retrieveDBTable(supabase, "materias")

# Get all professors as a list of Professor objects
professors = retrieveDBTable(supabase, "profesores")

# Access individual courses
for course in courses:
    print(f"{course.nombre} - Level {course.nivel}")

# Filter courses by level
level_1_courses = [c for c in courses if c.nivel == 1]
```

### Getting Formatted Class Lists

```python
from courses_functions import getClassesList

# Get organized class and lab lists for a specific semester
classes, labs, class_info, lab_info = getClassesList(courses, semester=1)

# classes and labs are lists for each day of the week
# class_info and lab_info are dictionaries mapping keys to course information
```

### Getting Professor Data

```python
from courses_functions import getProfessorsData

# Get professors as a dictionary mapping ID -> {name, email}
prof_data = getProfessorsData(supabase)

# Access professor info by ID
prof_id = "123456"
if prof_id in prof_data:
    print(prof_data[prof_id]['name'])   # Professor name
    print(prof_data[prof_id]['email'])  # Professor email
```

### Adding a Professor to the Database

```python
from courses_functions import addProfessorToDB
from professor import Professor

# Create a new professor
new_prof = Professor(
    nombre="Dr. Jane Smith",
    identificacion=654321,
    correo="jane.smith@university.edu",
    catedra=False,
    contratacion="PLANTA",
    formacion="MAESTRÍA"
)

# Add to database
addProfessorToDB(supabase, new_prof)
```

### Updating Schedules

```python
from courses_functions import update_schedule_in_db

# Update schedules in the database
# schedule_dict: dictionary with schedule information
# edited_keys: list of keys that were edited
# is_lab: boolean indicating if these are labs or classes

update_schedule_in_db(supabase, schedule_dict, edited_keys, is_lab=False)
```

### Deleting Classes

```python
from courses_functions import delete_class_in_db

# Delete classes by ID
deleted_ids = [123, 456, 789]
delete_class_in_db(supabase, deleted_ids)
```

## Serialization

### Converting to Dictionary

```python
# Convert a Course or Professor to a dictionary
course_dict = course.model_dump()

# Exclude None values and the id field (useful for insertions)
course_dict = course.model_dump(exclude_none=True, exclude={'id'})

# Only include specific fields
course_dict = course.model_dump(include={'nombre', 'nivel', 'horario'})
```

### Converting from Dictionary

```python
# Create an object from a dictionary
data = {
    'nombre': 'CÁLCULO I',
    'facultad': 2,
    'dependencia': 2,
    'ide': 'IIE',
    'materia': 3,
    'grupo': 1,
    'tipo': 'T-P',
    'es_lab': False,
    'nivel': 1,
    'horas_teoricas': 4,
    'horas_practicas': 2,
    'horas_tp': 0,
    'electiva': False,
    'es_dept': True,
    'horario': 'M10-12|J10-12',
    'profesor': [111111],
    'aula': 'B202'
}

course = Course(**data)
```

## Schedule Format

The `horario` field uses a specific format:
- Day codes: L (Lunes), M (Martes), W (Miércoles), J (Jueves), V (Viernes), S (Sábado)
- Format: `DayStartHour-EndHour` for single slot
- Multiple slots separated by `|`
- Examples:
  - `"L16-18"` - Monday 16:00 to 18:00
  - `"L16-18|M8-10"` - Monday 16-18 and Tuesday 8-10
  - `"MW10-12"` - Monday and Wednesday 10-12 (same time both days)

## Validation

### Course Validation
- All fields are validated based on their type
- `profesor` must be a list of integers
- Numeric fields are validated automatically

### Professor Validation
- `contratacion` must be one of the valid hiring types (automatically normalized to uppercase)
- `formacion` must be one of the valid education levels (automatically normalized to uppercase)
- Invalid values are replaced with "NO ESPECIFICADO" with a warning

## Type Safety

SQLModel provides full type safety:

```python
# IDE will autocomplete field names
course.nombre  # ✓
course.name    # ✗ Error: Course has no attribute 'name'

# Type checking works
course.nivel = 1      # ✓ int
course.nivel = "1"    # ✓ Will be converted to int
course.nivel = "abc"  # ✗ Will raise validation error
```

## Best Practices

1. **Always validate data** - SQLModel automatically validates, but check the types you're passing
2. **Use the models** - Don't create raw dictionaries, use Course/Professor objects
3. **Handle None values** - Remember that `id` is Optional and will be None for new objects
4. **Use get_codigo()** - For course codes, use the method instead of concatenating manually
5. **Check database responses** - Always verify that database operations succeed
6. **Use exclude parameters** - When inserting, exclude `id` and `None` values

## Common Patterns

### Filter courses by multiple criteria

```python
# Get all labs for level 1
level_1_labs = [c for c in courses if c.nivel == 1 and c.es_lab == True]

# Get all courses taught by a specific professor
prof_id = 123456
prof_courses = [c for c in courses if prof_id in c.profesor]
```

### Update a course

```python
# Modify course properties
course.horario = "L14-16|M14-16"
course.profesor = [123456, 789012]
course.aula = "C301"

# Then update in the database using update_schedule_in_db
```

### Create a lab variant

```python
# Create a lab version of a theory course
lab_course = Course(
    nombre=course.nombre,
    facultad=course.facultad,
    dependencia=course.dependencia,
    ide=course.ide,
    materia=course.materia,
    grupo=course.grupo,
    tipo=course.tipo,
    es_lab=True,  # Mark as lab
    nivel=course.nivel,
    horas_teoricas=0,
    horas_practicas=course.horas_practicas,
    horas_tp=course.horas_tp,
    electiva=course.electiva,
    es_dept=course.es_dept,
    horario="L14-17",  # Different schedule
    profesor=course.profesor,
    aula="LAB-01"  # Different room
)
```
