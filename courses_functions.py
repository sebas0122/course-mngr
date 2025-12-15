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

from dotenv import load_dotenv
load_dotenv()

import os

from supabase import create_client
import pandas as pd
from course import Course
from professor import Professor

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
    days_dict = {"L": "Lunes", "M": "Martes", "W": "Miércoles", "J": "Jueves", "V": "Viernes", "S": "Sábado", "D": "Domingo"} ##< Dictionary to map letters to days in Spanish
    days_hours_string = days_hours_string.replace(" ", "") ##< Remove spaces from the string
    days_hours_list = days_hours_string.split("|") ##< Split the string by "|"
    days = []
    start_hours = []
    class_duration = []
    for sch in days_hours_list:
        if sch != "":
            if sch[1] not in days_dict:
                days.append(days_dict[sch[0]]) ##< Add the day to the list
                start_hours.append(sch[1:].split("-")[0]) ##< Add the start hour to the list
                class_duration.append(int(sch[1:].split("-")[1]) - int(sch[1:].split("-")[0])) ##< Add the class duration to the list
            else:
                days.append(days_dict[sch[0]]) ##< Add the day to the list
                days.append(days_dict[sch[1]]) ##< Add the second day to the list 
                start_hours.append(sch[2:].split("-")[0]) ##< Add the start hour to the list
                start_hours.append(sch[2:].split("-")[0]) ##< Add the start hour to the list again for the second day
                class_duration.append(int(sch[2:].split("-")[1]) - int(sch[2:].split("-")[0])) ##< Add the class duration to the list
                class_duration.append(int(sch[2:].split("-")[1]) - int(sch[2:].split("-")[0])) ##< Add the class duration to the list again for the second day

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
        if "|" in days_hours_string: ##< Check if the string contains "|"
            _, _, x = getClassSchedule(days_hours_string) ##< Get the class duration
            return int(sum(x)) ##< Return the total number of hours
        else:
            letters = ["L", "M", "W", "J", "V", "S", "D"] ##< List of letters representing days
            if days_hours_string[1] in letters: ##< Check if the second character is a letter
                x = days_hours_string[2:].split("-") ##< Split the string to get the start and end hours
            else:
                x = days_hours_string[1:].split("-") ##< Split the string to get the start and end hours
            return int(x[1]) - int(x[0]) ##< Return the difference between the end and start hours
    except:
        return 0 ##< Return 0 if there is an error in processing the string

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
    # Retrieve data from the specified table
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
            
            key = f'{nombre}\n[{grupo}]_{st_hours[i]}_{class_duration[i]}_{aula}'
            
            key_info = f'{nombre}_{st_hours[i]}_{class_duration[i]}_{days[i]}_{aula}'  # Unique key for class or lab info
            
            info = {
                'id': [id],
                'nombre': nombre,
                'facultad': course.facultad,
                'dependencia': course.dependencia,
                'materia': course.materia,
                'codigo': codigo,
                'profesor': profesor,
                'grupo': [grupo],
                'aula': aula,
                'nivel': course.nivel
                # add more fields as needed
            }
            
            if course.es_lab == False:  # If it's a class
                if key_info in class_info_dict:
                    # If the class already exists, update the info
                    gr = class_info_dict[key_info]['grupo']
                    old_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}_{aula}'

                    gr.append(grupo)  # Append the new group to the existing one
                    ids = class_info_dict[key_info]['id']
                    ids.append(id)  # Append the new id to the existing one
                    class_info_dict[key_info]['grupo'] = gr
                    class_info_dict[key_info]['id'] = ids

                    idx = classes_list[week_days.index(days[i])].index(old_key) # Find the index of the old key
                    new_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}_{aula}' # Create the new key with the updated groups
                    classes_list[week_days.index(days[i])][idx] = new_key # Update the classes list with the new key
                else:
                    class_info_dict[key_info] = info
                    classes_list[week_days.index(days[i])].append(key)
            else:
                if key_info in lab_info_dict:
                    # If the lab already exists, update the info
                    gr = lab_info_dict[key_info]['grupo']
                    old_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}_{aula}'

                    gr.append(grupo)
                    ids = lab_info_dict[key_info]['id']
                    ids.append(id)  # Append the new id to the existing one
                    lab_info_dict[key_info]['grupo'] = gr
                    lab_info_dict[key_info]['id'] = ids

                    idx = labs_list[week_days.index(days[i])].index(old_key) # Find the index of the old key
                    new_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}_{aula}' # Create the new key with the updated groups
                    labs_list[week_days.index(days[i])][idx] = new_key # Update the labs list with the new key
                else:
                    lab_info_dict[key_info] = info
                    labs_list[week_days.index(days[i])].append(key)

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
    name = parts[0]
    hour = int(parts[1])
    duration = int(parts[2])
    day = parts[3]
    return name, hour, duration, day

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
        name, hour, duration, day = parse_schedule_key(key)
        slot = format_slot(day, hour, duration)
        for group in data['grupo']:
            class_id = (data['id'][data['grupo'].index(group)] if len(data['id']) > 1 else data['id'][0], name, group)
            if class_id not in class_map:
                class_map[class_id] = {}
                class_map[class_id]["new_schedule"] = []
            class_map[class_id]["new_schedule"].append(slot)
            class_map[class_id]["new_professors"] = data['profesor']
            class_map[class_id]["new_room"] = data['aula']
            class_map[class_id]["new_fac"] = data['facultad']
            class_map[class_id]["new_dep"] = data['dependencia']
            class_map[class_id]["new_mat"] = data['materia']
            class_map[class_id]["new_level"] = data['nivel'] if 'nivel' in data else 0

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
    only_edited_dict = {k: v for k, v in schedule_dict.items() if k in c_edited}
    print("Only edited schedule dict:", only_edited_dict)
    # 1. Parse and format
    class_map = build_schedule_map(only_edited_dict)

    for (id, subject_name, group), slots in class_map.items():
        formatted_schedule = '|'.join(sorted(slots["new_schedule"]))  # example: "L16-18|W8-10"
        if id != 0:
            response = (
                supabase
                .table("materias")
                .update({
                    "horario": formatted_schedule,
                    "profesor": slots["new_professors"],
                    "aula": slots["new_room"]
                    })
                .eq("nombre", subject_name)
                .eq("grupo", group)
                .eq("es_lab", is_lab)
                .execute()
            )
        else:
            response = (
                supabase
                .table("materias")
                .insert({
                    "nombre": subject_name,
                    "facultad": slots['new_fac'],
                    "dependencia": slots['new_dep'],
                    "ide": 'IIE',
                    "materia": slots['new_mat'],
                    "grupo": group,
                    "tipo": 'T-P',
                    "es_lab": is_lab,
                    "nivel": slots['new_level'],
                    "horas_teoricas": 4,
                    "horas_practicas": 3,
                    "horas_tp": 0,
                    "electiva": False,
                    "es_dept": True,
                    "horario": formatted_schedule,
                    "profesor": slots["new_professors"],
                    "aula": slots["new_room"]
                    })
                .execute()
            )
        if response.count == None:
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
        print(f"Deleting {id_to_delete}...")
        response = (
            supabase
            .table("materias")
            .delete()
            .eq("id", id_to_delete)
            .execute()
        )
        if response.count == None:
            print(f"Deleted {id_to_delete} successfully!")
        else:
            print(f"Error deleting {id_to_delete}.")

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