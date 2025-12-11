from dotenv import load_dotenv
load_dotenv()

import os

from supabase import create_client
import pandas as pd
from course import Course
from professor import Professor

## getClassSchedule function
# This function takes a string with the format "L1-2|M3-4|W5-6" and returns a list of days, start hours, and class duration.
# It splits the string by "|" and then processes each part to extract the day, start hour, and duration.
# It takes the following parameter:
# - days_hours_string: a string with the format "L1-2|M3-4|W5-6"
# Returns:
# - days: a list of days in Spanish (Lunes, Martes, etc.)
# - start_hours: a list of start hours for each class
# - class_duration: a list of class durations for each class
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

## getHoursLong function
# This function takes a string with the format "L1-2|M3-4|W5-6" and returns the total number of hours for all classes.
# It checks if the string contains "|" and processes it accordingly.
# It takes the following parameter:
# - days_hours_string: a string with the format "L1-2|M3-4|W5-6"
# Returns:
# - total_hours: an integer representing the total number of hours for all classes
# If the string is not in the expected format, it returns 0.
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

## connectSQL function
# This function connects to the Supabase database.
# Returns:
# - supabase: the Supabase client instance
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

## retrieveDBTable function
# This function retrieves data from the Supabase database.
# Takes:
# - supabase: the Supabase client instance
# - table_name: name of the table to retrieve data from
# Returns:
# - list of SQLModel objects (Course or Professor) if table_name is recognized
# - pandas DataFrame otherwise (for backwards compatibility)
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


## getClassesList function
# This function takes a list of Course objects and a semester level, and returns lists of classes and labs for each day of the week.
# It processes the courses to extract class information, including the name, code, professor, and group.
# It also creates dictionaries to map class and lab keys to their respective information.
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

# Mapping for weekdays
DAYS_MAP = {
    "Lunes": "L",
    "Martes": "M",
    "Miércoles": "W",
    "Jueves": "J",
    "Viernes": "V",
    "Sábado": "S"
}

def parse_schedule_key(key):
    # Example key: 'INFORMÁTICA I_16_2_Lunes'
    parts = key.split('_')
    name = parts[0]
    hour = int(parts[1])
    duration = int(parts[2])
    day = parts[3]
    return name, hour, duration, day

def format_slot(day, hour, duration):
    day_code = DAYS_MAP.get(day, '?')
    return f"{day_code}{hour}-{hour+duration}"

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