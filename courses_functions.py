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
    
def connectSQL():
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
    query = """
    SELECT * FROM materias
    """
    # Read the data into a pandas DataFrame
    df = pd.read_sql(query, engine)
    return df

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


def getClassesList(df, semester):
    df_semestre_1 = df[df['nivel'] == semester]

    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    classes_list = [[],[],[],[],[],[]]
    labs_list = [[],[],[],[],[],[]]

    for index, row in df_semestre_1.iterrows():
        # Get the values of the columns "codigo" and "nombre"
        horario = row['horario']
        days, st_hours, class_duration = getClassSchedule(horario)
        nombre = row['nombre']
        for i in range(len(days)):
            if row['es_lab'] == False:
                if f'{nombre}_{st_hours[i]}_{class_duration[i]}' not in classes_list[week_days.index(days[i])]:
                    # Append the class to the corresponding day in the classes_list
                    classes_list[week_days.index(days[i])].append(f'{nombre}_{st_hours[i]}_{class_duration[i]}')

                    # Insert blank slots for spacing between classes
                    day_classes = classes_list[week_days.index(days[i])]

                    # Ensure sorting is done before inserting blanks
                    day_classes.sort(key=lambda x: int(x.split('_')[1]))
            else:
                if f'{nombre}_{st_hours[i]}_{class_duration[i]}' not in labs_list[week_days.index(days[i])]:
                    # Append the lab to the corresponding day in the labs_list
                    labs_list[week_days.index(days[i])].append(f'{nombre}_{st_hours[i]}_{class_duration[i]}')

                    # Insert blank slots for spacing between labs
                    day_labs = labs_list[week_days.index(days[i])]

                    # Ensure sorting is done before inserting blanks
                    day_labs.sort(key=lambda x: int(x.split('_')[1]))

    classes_list = reorganizeClassesList(classes_list)
    labs_list = reorganizeClassesList(labs_list)  

    return classes_list, labs_list