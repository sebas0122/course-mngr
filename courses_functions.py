from sqlalchemy import create_engine
from sqlalchemy.engine import URL
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
# This function connects to a PostgreSQL database and retrieves data from the "materias" table.
# It uses SQLAlchemy to create a connection and pandas to read the data into a DataFrame.
# It takes the following parameter:
# - table: the name of the table to retrieve data from
def connectSQL(table):
    uid = 'postgres'
    pwd = 'UdeA_elecNtelDPT*'
    host = 'localhost'
    port = '5432'
    db = 'programacion'

    # Create a connection string
    connection_string = f'postgresql://{uid}:{pwd}@{host}:{port}/{db}'
    # Create a database engine
    engine = create_engine(connection_string)

    # Execute a query to get the data from table "materias"
    query = f"""
    SELECT * FROM {table}
    """
    # Read the data into a pandas DataFrame
    df = pd.read_sql(query, engine)
    return df

## reorganizeClassesList function
# This function takes a list of classes for each day and reorganizes it by inserting blanks where necessary.
# It ensures that the classes are sorted by start hour and that there are no gaps between classes.
# It takes the following parameter:
# - cl_li: a list of lists, where each inner list contains class strings in the format "class_startHour_duration"
# Returns:
# - classes_list: a list of lists, where each inner list contains reorganized class strings
# The reorganized classes are sorted by start hour and have blanks inserted where necessary.
def reorganizeClassesList(cl_li):

    classes_list = cl_li.copy()

    for day_classes in classes_list:
        # Insert blank at the start if first class starts after 6
        if day_classes != []:
            first_hour = int(day_classes[0].split('_')[1])
            if first_hour > 6:
                day_classes.insert(0, f'blank_{first_hour - 6}')
            # Insert blanks between classes
            j = 1
            while j < len(day_classes):
                prev_hour = int(day_classes[j - 1].split('_')[1])
                prev_hour_dur = 0
                if not day_classes[j - 1].startswith('blank'):
                    prev_hour_dur = int(day_classes[j - 1].split('_')[2])
                curr_hour = int(day_classes[j].split('_')[1])
                # print(f'Checking gap between {day_classes[j - 1]} and {day_classes[j]}: prev_hour={prev_hour}, curr_hour={curr_hour}, prev_hour_dur={prev_hour_dur}')
                if curr_hour - prev_hour - prev_hour_dur> 0:
                    # Only insert blank if not already a blank
                    if not day_classes[j - 1].startswith('blank') and not day_classes[j].startswith('blank'):
                        day_classes.insert(j, f'blank_{curr_hour - prev_hour - prev_hour_dur}')
                        j += 1
                j += 1

                    
    # Replace class duration with the correct duration for all classes in the day's list
    for cl in classes_list:
        for k in range(len(cl)):
            parts = cl[k].split('_')
            if not parts[0].startswith('blank'):
                # Set duration to the original duration for this class
                cl[k] = f"{parts[0]}_{parts[2]}"
    
    return classes_list

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
            key = f'{nombre}\n[{grupo}]_{st_hours[i]}_{class_duration[i]}'
            key_info = f'{nombre}_{st_hours[i]}_{class_duration[i]}_{days[i]}'  # Unique key for class or lab info
            info = {
                'id': id,
                'nombre': nombre,
                'codigo': codigo,
                'profesor': profesor,
                'grupo': [grupo],
                'aula': aula
                # add more fields as needed
            }
            if row['es_lab'] == False:
                if key_info in class_info_dict:
                    if grupo not in class_info_dict[key_info]['grupo']:
                        # If the class already exists, update the info
                        gr = class_info_dict[key_info]['grupo']
                        old_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}'

                        gr.append(grupo)  # Append the new group to the existing one
                        class_info_dict[key_info]['grupo'] = gr

                        
                        idx = classes_list[week_days.index(days[i])].index(old_key)
                        new_key = f'{nombre}\n{gr}_{st_hours[i]}_{class_duration[i]}'
                        classes_list[week_days.index(days[i])][idx] = new_key
                elif key not in classes_list[week_days.index(days[i])]:
                    classes_list[week_days.index(days[i])].append(key)
                    class_info_dict[key_info] = info
                    day_classes = classes_list[week_days.index(days[i])]
                    day_classes.sort(key=lambda x: int(x.split('_')[1]))
            else:
                if key in lab_info_dict:
                    if grupo not in lab_info_dict[key_info]['grupo']:
                        # If the lab already exists, update the info
                        gr = lab_info_dict[key_info]['grupo']
                        gr.append(grupo)  # Append the new group to the existing one
                        lab_info_dict[key_info]['grupo'] = gr
                if key not in labs_list[week_days.index(days[i])]:
                    labs_list[week_days.index(days[i])].append(key)
                    lab_info_dict[key_info] = info
                    day_labs = labs_list[week_days.index(days[i])]
                    day_labs.sort(key=lambda x: int(x.split('_')[1]))

    classes_list = reorganizeClassesList(classes_list)
    labs_list = reorganizeClassesList(labs_list)  

    return classes_list, labs_list, class_info_dict, lab_info_dict

def getProfessorsData():
    dataframe = connectSQL("profesores")  # Ensure the connection is established
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
            class_id = (name, group)
            if class_id not in class_map:
                class_map[class_id] = []
            class_map[class_id].append(slot)
    return class_map

def update_schedule_in_db(schedule_dict, is_lab):
    # 1. Parse and format
    class_map = build_schedule_map(schedule_dict)    

    uid = 'postgres'
    pwd = 'UdeA_elecNtelDPT*'
    host = 'localhost'
    port = '5432'
    db = 'programacion'

    # Create a connection string
    connection_string = f'postgresql://{uid}:{pwd}@{host}:{port}/{db}'
    # Create a database engine
    engine = create_engine(connection_string)
    
    # Update query
    query = """
        UPDATE materias
        SET horario = %s
        WHERE nombre = %s AND grupo = %s AND es_lab = %s;
    """

    # Perform the update
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        for (subject_name, group), slots in class_map.items():
            formatted_schedule = '|'.join(sorted(slots))  # example: "L16-18|W8-10"
            values = (formatted_schedule, subject_name, group, is_lab) 
            cursor.execute(query, values)

        conn.commit()
    except Exception as e:
        print("Error while updating schedules:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()