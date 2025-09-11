from dotenv import load_dotenv
load_dotenv()

import os

from supabase import create_client
import pandas as pd

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

## retrieveDBCourses function
# This function retrieves course data from the Supabase database.
# Takes:
# - supabase: the Supabase client instance
# Returns:
# - df: a pandas DataFrame containing the course data
def retrieveDBTable(supabase, table_name):
    # Retrieve data from the specified table
    data = supabase.table(table_name).select("*").execute()

    df = pd.DataFrame(data.data)
    return df


## getClassesList function
# This function takes a DataFrame and a semester level, and returns lists of classes and labs for each day of the week.
# It processes the DataFrame to extract class information, including the name, code, professor, and group.
# It also creates dictionaries to map class and lab keys to their respective information.
def getClassesList(df, semester):
    df_semestre_1 = df[df['nivel'] == semester]

    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    classes_list = [[],[],[],[],[],[]]
    labs_list = [[],[],[],[],[],[]]
    class_info_dict = {}  # NEW: maps 'class_2' -> info dict
    lab_info_dict = {}    # NEW: maps 'lab_2' -> info dict

    for index, row in df_semestre_1.iterrows():
        id = row['id']
        horario = row['horario']
        days, st_hours, class_duration = getClassSchedule(horario)
        nombre = row['nombre']
        codigo = str(row['facultad']) + str(row['dependencia']) + str(row['materia'])
        profesor = row['profesor']  # adjust to your column name
        grupo = row['grupo']  # adjust to your column name
        aula = row['aula']  # adjust to your column name
        for i in range(len(days)):
            
            key = f'{nombre}\n[{grupo}]_{st_hours[i]}_{class_duration[i]}_{aula}'
            
            key_info = f'{nombre}_{st_hours[i]}_{class_duration[i]}_{days[i]}_{aula}'  # Unique key for class or lab info
            
            info = {
                'id': id,
                'nombre': nombre,
                'codigo': codigo,
                'profesor': profesor,
                'grupo': [grupo],
                'aula': aula
                # add more fields as needed
            }
            
            if row['es_lab'] == False:  # If it's a class
                if key_info in class_info_dict:
                    # If the class already exists, update the info
                    gr = class_info_dict[key_info]['grupo']
                    old_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}_{aula}'

                    gr.append(grupo)  # Append the new group to the existing one
                    class_info_dict[key_info]['grupo'] = gr


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
                    lab_info_dict[key_info]['grupo'] = gr

                    idx = labs_list[week_days.index(days[i])].index(old_key) # Find the index of the old key
                    new_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}_{aula}' # Create the new key with the updated groups
                    labs_list[week_days.index(days[i])][idx] = new_key # Update the labs list with the new key
                else:
                    lab_info_dict[key_info] = info
                    labs_list[week_days.index(days[i])].append(key)

    return classes_list, labs_list, class_info_dict, lab_info_dict

def getProfessorsData(supabase):
    dataframe = retrieveDBTable(supabase, "profesores")  # Ensure the connection is established
    """
    This function extracts professors' data from the DataFrame and returns it as a list of dictionaries.
    Each dictionary contains the professor's ID, name, and email.
    """
    professors = {}
    df_prof_id = dataframe["identificacion"]
    df_prof_name = dataframe["nombre"]
    df_prof_email = dataframe["correo"]

    for i in range(len(df_prof_id)):
        if pd.notna(df_prof_id[i]) and pd.notna(df_prof_name[i]) and pd.notna(df_prof_email[i]):
            professors[str(int(df_prof_id[i]))] = {
                'name': df_prof_name[i].strip(),
                'email': df_prof_email[i].strip()
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
            class_id = (data['id'], name, group)
            if class_id not in class_map:
                class_map[class_id] = {}
                class_map[class_id]["new_schedule"] = []
            class_map[class_id]["new_schedule"].append(slot)
            class_map[class_id]["new_proffessors"] = data['profesor']
            class_map[class_id]["new_room"] = data['aula']
    return class_map

def update_schedule_in_db(supabase, schedule_dict, c_edited, is_lab):
    only_edited_dict = {k: v for k, v in schedule_dict.items() if k in c_edited}
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
                    "profesor": slots["new_proffessors"],
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
                    "facultad": 25,
                    "dependencia": 98,
                    "ide": 'IIE',
                    "materia": 000,
                    "grupo": group,
                    "tipo": 'T-P',
                    "es_lab": is_lab,
                    "nivel": 1,
                    "horas_teoricas": 4,
                    "horas_practicas": 3,
                    "horas_tp": 0,
                    "electiva": False,
                    "es_dept": True,
                    "horario": formatted_schedule,
                    "profesor": slots["new_proffessors"],
                    "aula": slots["new_room"]
                    })
                .execute()
            )
        if response.count == None:
            print("Saved successfully!")
        else:
            print("Error saving data.")