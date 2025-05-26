from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pandas as pd
from courses_functions import getClassSchedule

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

# Print the DataFrame where the column "nivel" is 1
df_semestre_1 = df[df['nivel'] == 6]
print(df_semestre_1)

week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

classes_list = [
    [],
    [],
    [],
    [],
    [],
    []
]

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


print("Classes list: ", classes_list)