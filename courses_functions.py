##
# @file courses_functions.py
# @brief Database and course management utility functions
#
# This module provides core functionality for interacting with the Supabase database,
# parsing course schedules, and managing course data. It includes functions for
# connecting to the database, retrieving and processing course information, updating
# schedules, and managing professors.
#
# @author Nelson Parra (nelson.parra@udea.edu.co)
# @date 2025

import os
import re
import sys
from dotenv import load_dotenv

# Load .env from beside the .exe (when frozen) or beside this script (dev)
_base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                             else os.path.abspath(__file__))
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print(f"Loading .env from: {_base_dir}")
load_dotenv(dotenv_path=os.path.join(_base_dir, '.env'))

from supabase import create_client
import pandas as pd
from course import Course
from professor import Professor

DAY_LETTER_TO_NAME = {
    "L": "Lunes",
    "M": "Martes",
    "W": "Miércoles",
    "J": "Jueves",
    "V": "Viernes",
    "S": "Sábado",
}

DAY_NAME_TO_LETTER = {v: k for k, v in DAY_LETTER_TO_NAME.items()}

DAY_ORDER = {"L": 0, "M": 1, "W": 2, "J": 3, "V": 4, "S": 5}

_TOKEN_RE = re.compile(r"^([LMWJVS]+)(\d{1,2})-(\d{1,2})$")

def parse_schedule_slots(schedule_raw):
    if schedule_raw is None:
        raise ValueError("Horario vacío (None).")

    s = str(schedule_raw).strip().replace(" ", "")
    if not s:
        raise ValueError("Horario vacío.")

    tokens = [t for t in s.split("|") if t]
    if not tokens:
        raise ValueError("Horario sin bloques válidos.")

    slots = []
    for token in tokens:
        m = _TOKEN_RE.match(token)
        if not m:
            raise ValueError(f"Formato de bloque inválido: {token}")

        day_letters, start_txt, end_txt = m.groups()
        start = int(start_txt)
        end = int(end_txt)

        if end <= start:
            raise ValueError(f"Rango inválido en bloque {token}: fin <= inicio")
        if start < 0 or end > 24:
            raise ValueError(f"Rango horario fuera de límites en bloque {token}")

        for d in day_letters:
            if d not in DAY_LETTER_TO_NAME:
                raise ValueError(f"Día inválido en bloque {token}: {d}")
            slots.append((d, start, end))

    slots.sort(key=lambda x: (DAY_ORDER[x[0]], x[1], x[2]))
    return slots

def normalize_schedule(schedule_raw):
    slots = parse_schedule_slots(schedule_raw)
    return "|".join(f"{d}{start}-{end}" for d, start, end in slots)

##
# @brief Parse schedule string into days, start hours, and durations
#
# This function takes a schedule string in format "L1-2|M3-4|W5-6" where L/M/W/J/V/S/D
# represent days of the week (Spanish) and numbers represent hours. It splits the string
# and extracts schedule information for each class session.
#
# Format examples:
# - "L16-18" = Monday from 16:00 to 18:00 (2 hours)
# - "LM8-10" = Monday and Tuesday from 8:00 to 10:00 (2 hours each)
# - "L16-18|M8-10" = Monday 16-18 and Tuesday 8-10
#
# @param days_hours_string Schedule string with format "L1-2|M3-4|W5-6"
# @return Tuple containing:
#         - days: List of day names in Spanish (Lunes, Martes, etc.)
#         - start_hours: List of start hours for each class
#         - class_duration: List of class durations in hours for each class
def getClassSchedule(days_hours_string):
    days = []
    start_hours = []
    class_duration = []

    slots = parse_schedule_slots(days_hours_string)
    for d, start, end in slots:
        days.append(DAY_LETTER_TO_NAME[d])
        start_hours.append(str(start))
        class_duration.append(end - start)

    return days, start_hours, class_duration

##
# @brief Calculate total hours from a schedule string
#
# This function processes a schedule string and returns the total number of hours
# for all class sessions. It handles both single entries ("L16-18") and multiple
# entries separated by pipes ("L16-18|M8-10").
#
# @param days_hours_string Schedule string with format "L1-2|M3-4|W5-6"
# @return Integer representing total number of hours, or 0 if parsing fails
def getHoursLong(days_hours_string):
    try:
        slots = parse_schedule_slots(days_hours_string)
        return sum(end - start for _, start, end in slots)
    except Exception as e:
        print(f"Horario inválido en getHoursLong: {days_hours_string} -> {e}")
        return 0

##
# @brief Establish connection to Supabase database
#
# This function creates and returns a Supabase client instance using credentials
# from environment variables (SUPABASE_URL and SUPABASE_KEY). The .env file must
# be present in the project root with these variables defined.
#
# @return Supabase client instance if successful, None if connection fails
def connectSQL():
    try:
        # Connect to the Supabase database
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase = create_client(url, key)

        return supabase
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

##
# @brief Retrieve and convert database table data to objects
#
# This function retrieves all records from a specified Supabase table and converts
# them to appropriate SQLModel objects (Course or Professor) if recognized, or returns
# a pandas DataFrame for backwards compatibility with unknown tables.
#
# @param supabase Supabase client instance
# @param table_name Name of the table to retrieve ("materias" or "profesores")
# @return List of SQLModel objects (Course or Professor) for recognized tables,
#         pandas DataFrame for other tables
def retrieveDBTable(supabase, table_name):
    if supabase is None:
        raise ConnectionError(
            "No se pudo conectar a la base de datos. "
            "Verifica que el archivo .env esté presente junto al ejecutable "
            "y que las credenciales SUPABASE_URL y SUPABASE_KEY sean correctas."
        )
    data = supabase.table(table_name).select("*").execute()

    # Convert to SQLModel objects if possible
    if table_name == "materias":
        return [Course(**row) for row in data.data]
    elif table_name == "profesores":
        return [Professor(**row) for row in data.data]
    else:
        # Return DataFrame for unknown tables (backwards compatibility)
        df = pd.DataFrame(data.data)
        return df


##
# @brief Process course list and organize by schedule
#
# This function takes a list of Course objects, filters them by semester level,
# and organizes them into weekly schedule grids. It creates separate lists for
# theory classes and labs, grouped by day of the week. Courses with the same
# schedule are grouped together with combined group numbers.
#
# @param courses_list List of Course SQLModel objects from database
# @param semester Semester/level number to filter courses (1-10, or 21+ for electives)
# @return Tuple containing:
#         - classes_list: List of 6 lists (one per weekday) with class schedule strings
#         - labs_list: List of 6 lists (one per weekday) with lab schedule strings
#         - class_info_dict: Dict mapping schedule keys to class information
#         - lab_info_dict: Dict mapping schedule keys to lab information
def getClassesList(courses_list, semester):
    # Filter courses by semester level
    courses_semester = [course for course in courses_list if course.nivel == semester]

    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    classes_list = [[],[],[],[],[],[]]
    labs_list = [[],[],[],[],[],[]]
    class_info_dict = {}  # maps key -> info dict
    lab_info_dict = {}    # maps key -> info dict

    for course in courses_semester:
        id = course.id
        horario = course.horario
        days, st_hours, class_duration = getClassSchedule(horario)
        nombre = course.nombre
        codigo = course.get_codigo()
        profesor = course.profesor
        grupo = course.grupo
        aula = course.aula
        
        for i in range(len(days)):
            # Determinate the type of the course (lab or theory) to create the key and assign it to the widget for later identification when editing/deleting
            tipo = "1" if course.es_lab else "0"
            # Use the day to find the index of the corresponding list in classes_list or labs_list
            day_idx = week_days.index(days[i])
            # Build the key for the course/lab using codigo, start hour, duration, day, aula and type (lab or theory)
            # if already exists, add the group to the existing key, if not create a new key with the group, and in both cases add the id to the info dict for later use when editing/deleting
            if day_idx >= len(classes_list):
                # La UI actual muestra 6 días (L-S). Ignorar Domingo para no romper.
                continue
            if course.es_lab:
                info_dict = lab_info_dict
            else:
                info_dict = class_info_dict

            # key_base uses codigo for unique DB-level identification
            key_base = f"{codigo}_{st_hours[i]}_{class_duration[i]}_{days[i]}_{aula}_{tipo}"
            
            # merge_key uses nombre instead of codigo, so different pensum versions
            # of the same course (same name, same slot) get merged into one widget
            merge_key = f"{nombre}_{st_hours[i]}_{class_duration[i]}_{days[i]}_{aula}_{tipo}"

            # Check if there's already an entry with the same merge_key
            existing_key_base = None
            for existing_kb, existing_info in info_dict.items():
                existing_merge = f"{existing_info['nombre']}_{existing_info['hora_inicio']}_{existing_info['duracion']}_{existing_info['dia']}_{existing_info['aula']}_{existing_kb.split('_')[-1]}"
                if existing_merge == merge_key:
                    existing_key_base = existing_kb
                    break

            if existing_key_base is not None:
                # Mantener alineacion grupo <-> id y conservar codigos fusionados
                existing = info_dict[existing_key_base]

                if id in existing['id']:
                    idx_id = existing['id'].index(id)
                    if idx_id < len(existing['grupo']):
                        existing['grupo'][idx_id] = grupo
                    else:
                        existing['grupo'].append(grupo)
                else:
                    existing['id'].append(id)
                    existing['grupo'].append(grupo)

                if 'codigos' not in existing:
                    existing['codigos'] = [existing['codigo']]
                if codigo not in existing['codigos']:
                    existing['codigos'].append(codigo)
            else:
                info = {
                    'id': [id],
                    'nombre': nombre,
                    'facultad': course.facultad,
                    'dependencia': course.dependencia,
                    'materia': course.materia,
                    'codigo': codigo,
                    'codigos': [codigo],
                    'profesor': profesor,
                    'grupo': [grupo],
                    'aula': aula,
                    'nivel': course.nivel,
                    'hora_inicio': st_hours[i],     
                    'duracion': class_duration[i],   
                    'dia': days[i]    
                }
                info_dict[key_base] = info

    # Build the classes_list and labs_list using the info dicts
    added_classes = set()
    for key_base, info in class_info_dict.items():
        day_idx = week_days.index(info['dia'])
        grupos_str = "-".join(str(g) for g in sorted(set(info['grupo'])))
        widget_key = f"{info['codigo']}_{grupos_str}_0"
        pair = (widget_key, day_idx)
        if pair not in added_classes:
            added_classes.add(pair)
            classes_list[day_idx].append(widget_key)

    added_labs = set()
    for key_base, info in lab_info_dict.items():
        day_idx = week_days.index(info['dia'])
        grupos_str = "-".join(str(g) for g in sorted(set(info['grupo'])))
        widget_key = f"{info['codigo']}_{grupos_str}_1"
        pair = (widget_key, day_idx)
        if pair not in added_labs:
            added_labs.add(pair)
            labs_list[day_idx].append(widget_key)

    return classes_list, labs_list, class_info_dict, lab_info_dict

##
# @brief Extract and format professor data from database
#
# This function retrieves professor information from the database and formats it
# into a dictionary for easy lookup. Each entry maps a professor's identification
# number to their name and email address.
#
# @param supabase Supabase client instance
# @return Dictionary where keys are professor IDs (as strings) and values are dicts
#         containing 'name' and 'email' keys
def getProfessorsData(supabase):
    """
    This function extracts professors' data from the database and returns it as a dictionary.
    Each entry maps the professor's ID (as string) to a dictionary containing their name and email.
    """
    professors_list = retrieveDBTable(supabase, "profesores")  # Returns list of Professor objects
    
    professors = {}
    for prof in professors_list:
        if prof.identificacion and prof.nombre and prof.correo:
            professors[str(prof.identificacion)] = {
                'name': prof.nombre.strip(),
                'email': prof.correo.strip()
            }

    return professors

##< Mapping dictionary from Spanish day names to single-letter codes
DAYS_MAP = {
    "Lunes": "L",
    "Martes": "M",
    "Miércoles": "W",
    "Jueves": "J",
    "Viernes": "V",
    "Sábado": "S"
}

##
# @brief Parse schedule key into components
#
# Extracts schedule information from a key string format used internally.
#
# @param key Schedule key in format "COURSE_NAME_HOUR_DURATION_DAY"
# @return Tuple of (name, hour, duration, day)
def parse_schedule_key(key):
    # Example key: 'INFORMÁTICA I_16_2_Lunes'
    parts = key.split('_')
    if len(parts) < 6:
        return None
    try:
        codigo = parts[0]
        hour = int(parts[1])
        duration = int(parts[2])
        day = parts[3]
        tipo = parts[-1]
        room = "_".join(parts[4:-1])  # safe if room contains underscores
        return codigo, hour, duration, day, room, tipo
    except Exception:
        return None

##
# @brief Format schedule slot into compact notation
#
# Converts day, hour, and duration into compact schedule format like "L16-18".
#
# @param day Day name in Spanish (Lunes, Martes, etc.)
# @param hour Start hour (6-22)
# @param duration Duration in hours
# @return Formatted slot string (e.g., "L16-18")
def format_slot(day, hour, duration):
    day_code = DAYS_MAP.get(day, '?')
    return f"{day_code}{hour}-{hour+duration}"

##
# @brief Build schedule map from schedule dictionary
#
# Processes a schedule information dictionary and creates a structured map
# organizing courses by ID, name, and group with their new schedule details.
#
# @param schedule_dict Dictionary mapping schedule keys to course information
# @return Dictionary mapping (id, name, group) tuples to schedule details
def build_schedule_map(schedule_dict):
    class_map = {}
    for key, data in schedule_dict.items():
        # key format: codigo_hora_duracion_dia_aula_tipo
        for idx, group in enumerate(data['grupo']):
            if idx >= len(data['id']):
                print(f"WARNING: desalineacion grupo/id en key={key} grupo={group}")
                continue
            id_ = data['id'][idx] # ← CAMBIO: usar ID en lugar de (id, nombre, grupo)

            if id_ != 0:
                class_id = ("db", id_)
            else:
                class_id = (
                    "new",
                    data.get('nombre', ''),
                    group,
                    data.get('aula', ''),
                    idx
                )
            
            if class_id not in class_map:
                class_map[class_id] = {
                    "new_schedule": [],
                    "new_professors": data['profesor'],
                    "new_room": data['aula'],
                    "nombre": data['nombre'],
                    "grupo": group,
                    "es_lab": data.get('es_lab', False),
                    "new_fac": data.get('facultad', ''),
                    "new_dep": data.get('dependencia', ''),
                    "new_mat": data.get('materia', ''),
                    "new_level": data.get('nivel', 0),
                    "db_id": id_,
                }
            
            # Calcular nuevo slot
            hour = int(data['hora_inicio'])
            duration = int(data['duracion'])
            day = data['dia']
            
            slot = format_slot(day, int(hour), int(duration))
            if slot not in class_map[class_id]["new_schedule"]:
                class_map[class_id]["new_schedule"].append(slot)

    return class_map

##
# @brief Update course schedules in the database
#
# This function takes modified schedule information and updates the database records.
# It processes only the courses that have been edited (tracked in c_edited list),
# formats their schedules into the database format, and performs UPDATE or INSERT
# operations as needed.
#
# @param supabase Supabase client instance
# @param schedule_dict Dictionary mapping schedule keys to course information
# @param c_edited List of schedule keys that have been modified
# @param is_lab Boolean indicating whether these are lab sessions (True) or classes (False)
def update_schedule_in_db(supabase, schedule_dict, c_edited, is_lab):
    print("Schedule list to update:", c_edited)
    print("schedule_dict keys:", list(schedule_dict.keys()))
    print("c_edited:", c_edited)

    # 1) IDs afectados por keys editados
    edited_ids = set()
    for k in c_edited:
        if k in schedule_dict:
            for id_ in schedule_dict[k].get('id', []):
                if id_ != 0:
                    edited_ids.add(id_)

    # 2) Incluir todos los bloques que compartan esos IDs
    only_edited_dict = {}
    for k, v in schedule_dict.items():
        key_is_edited = k in c_edited
        shares_id = bool(edited_ids.intersection(set(v.get('id', []))))
        if key_is_edited or shares_id:
            only_edited_dict[k] = v

    # 3) Warning de integridad (ahora sí, con dict ya construido)
    for k, v in only_edited_dict.items():
        if len(v.get('grupo', [])) != len(v.get('id', [])):
            print(
                f"WARNING: grupo/id desalineado en {k}: "
                f"grupos={v.get('grupo')} ids={v.get('id')}"
            )

    print("Only edited schedule dict:", only_edited_dict)

    # 4) Parse y update/insert
    class_map = build_schedule_map(only_edited_dict)
    print("Class map to update:", class_map)

    for class_key, info in class_map.items():
        id_ = info["db_id"]

        try:
            formatted_schedule = normalize_schedule("|".join(info["new_schedule"]))
        except Exception:
            formatted_schedule = "|".join(info["new_schedule"])

        print("--------------------------------------------------------------")
        print("--------------------------------------------------------------")
        print("--------------------------------------------------------------")
        print(f"Formatted schedule: {formatted_schedule}")
        horas = getHoursLong(formatted_schedule)
        print(f"Calculated hours: {horas}")

        if id_ != 0:
            response = (
                supabase
                .table("materias")
                .update({
                    "horario": formatted_schedule,
                    "profesor": info["new_professors"],
                    "aula": info["new_room"],
                    "horas_teoricas": horas if not is_lab else 0,
                    "horas_practicas": horas if is_lab else 0
                })
                .eq("id", id_)
                .execute()
            )
        else:
            response = (
                supabase
                .table("materias")
                .insert({
                    "nombre": info["nombre"],
                    "facultad": info["new_fac"],
                    "dependencia": info["new_dep"],
                    "ide": "IIE",
                    "materia": info["new_mat"],
                    "grupo": info["grupo"],
                    "tipo": "T-P",
                    "es_lab": is_lab,
                    "nivel": info["new_level"],
                    "horas_teoricas": horas if not is_lab else 0,
                    "horas_practicas": horas if is_lab else 0,
                    "horas_tp": 0,
                    "electiva": False,
                    "es_dept": True,
                    "horario": formatted_schedule,
                    "profesor": info["new_professors"],
                    "aula": info["new_room"]
                })
                .execute()
            )

        if response.count is None:
            print("Saved successfully!")
        else:
            print("Error saving data.")

##
# @brief Delete courses from the database
#
# This function deletes course records from the database by their IDs.
# It iterates through the list of IDs to delete and performs a DELETE operation
# for each one.
#
# @param supabase Supabase client instance
# @param deleted_keys List of course IDs to delete from database
def delete_class_in_db(supabase, deleted_keys):
    for id_to_delete in deleted_keys:
        if id_to_delete == 0:
            print(f"Skipping id=0 (new unsaved course)")
            continue
        print(f"Deleting id={id_to_delete}...")
        # Primero poner horas a 0 para liberar carga del profesor
        supabase.table("materias").update({
            "horas_teoricas": 0,
            "horas_practicas": 0,
            "horas_tp": 0
        }).eq("id", id_to_delete).execute()

        # Luego eliminar el registro
        del_response = (
            supabase
            .table("materias")
            .delete()
            .eq("id", id_to_delete)
            .execute()
        )
        print(f"Deleted {id_to_delete} successfully!") 

##
# @brief Recalculate hours after widget removal
#           
# This function recalculates the hours for courses affected by the removal of a schedule widget.
# It retrieves the current schedule information, calculates the new hours by subtracting the hours of the deleted widget, and updates the database with the new hours for the affected courses.
#
# @param supabase Supabase client instance
# @param hours_deleted_widget Number of hours associated with the deleted widget
# @param keys_to_update List of schedule keys that need to have their hours updated
# @param semester Semester/level number to filter courses (default is 1)

def recalculate_hours_after_widget_removal(supabase, horas_eliminadas_por_id):
    # get all courses to find the ones that need to be updated
    all_courses = retrieveDBTable(supabase, "materias")
    for course in all_courses:
        id_ = course.id
        if id_ in horas_eliminadas_por_id:
            horas_a_restar = horas_eliminadas_por_id[id_]
            #bloque_a_eliminar = horas_eliminadas_por_id[id_].get('bloque', None)
            horario = getattr(course, "horario", "")
            current_hours = getHoursLong(horario)
            nuevas_horas = max(0, current_hours - horas_a_restar)
            es_lab = getattr(course, "es_lab", False)
            print("--------------------------------------------------------------")
            print("--------------------------------------------------------------")
            print(f"harario actual: {horario}")
            print(f"horas a restar: {horas_a_restar}")
            print(f"horas actuales: {current_hours}")
            print(f"nuevas horas: {nuevas_horas}")

            """bloques = horario.split('|') if horario else []
            if bloque_a_eliminar and bloque_a_eliminar in bloques:
                bloques.remove(bloque_a_eliminar)
            nuevo_horario = '|'.join(bloques)"""

            #print(f"nuevo horario: {nuevo_horario}")

            # update the course with the new hours
            response = (
                supabase
                .table("materias")
                .update({
                    "horas_teoricas": nuevas_horas if not es_lab else 0,
                    "horas_practicas": nuevas_horas if es_lab else 0,
                    #"horario": nuevo_horario
                })
                .eq("id", id_)
                .execute()
            )
            if getattr(response, "error", None):
                print(f"Error updating hours for id {id_}: {response.error}")
            else:
                print(f"Updated hours for id {id_} successfully!")

            """if response.count == None:
                print(f"Updated hours for id {id_} successfully!")
            else:
                print(f"Error updating hours for id {id_}.")"""
##
# @brief Add a new professor to the database
#
# This function inserts a new professor record into the database. It takes a
# Professor SQLModel object, converts it to a dictionary (excluding the id field),
# and inserts it into the profesores table.
#
# @param supabase Supabase client instance
# @param professor Professor SQLModel object to insert
def addProfessorToDB(supabase, professor):
    """
    Add a Professor SQLModel object to the database.
    Args:
        supabase: Supabase client instance
        professor: Professor SQLModel object
    """
    # Convert SQLModel object to dict, excluding None id
    prof_dict = professor.model_dump(exclude_none=True, exclude={'id'})
    
    response = (
        supabase
        .table("profesores")
        .insert(prof_dict)
        .execute()
    )
    if response.count == None:
        print("Professor added successfully!")
    else:
        print("Error adding professor.")