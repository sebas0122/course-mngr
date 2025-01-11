import pandas as pd

def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="PROGRAMACION_2025_1")
        print("Excel file read successfully!")
        return df
    except Exception as e:
        print(f"An error occurred: {e}")

def getClassSchedule(days_hours_string):
    days_dict = {"L": "Lunes", "M": "Martes", "W": "Miércoles", "J": "Jueves", "V": "Viernes", "S": "Sábado", "D": "Domingo"}
    days_hours_list = days_hours_string.split("|")
    days = []
    start_hours = []
    class_duration = []
    for sch in days_hours_list:
        if sch != "":
            if sch[1] not in days_dict:
                days.append(days_dict[sch[0]])
                start_hours.append(sch[1:].split("-")[0])
                class_duration.append(int(sch[1:].split("-")[1]) - int(sch[1:].split("-")[0]))
            else:
                days.append(days_dict[sch[0]])
                days.append(days_dict[sch[1]])
                start_hours.append(sch[2:].split("-")[0])
                class_duration.append(int(sch[2:].split("-")[1]) - int(sch[2:].split("-")[0]))

    return days, start_hours, class_duration

def getHoursLong(days_hours_string):
    if "|" in days_hours_string:
        _, _, x = getClassSchedule(days_hours_string)
        return int(sum(x))
    else:
        print(days_hours_string, days_hours_string[2:])
        x = days_hours_string[1:].split("-")
        return int(x[1]) - int(x[0])

def getCleanData(dataframe):

    courses = []
    for_db = []
    
    df_fac   = dataframe["FAC"]
    df_dep   = dataframe["DEP"]
    df_ide   = dataframe["IDE"]
    df_mat   = dataframe["MAT"]
    df_group = dataframe["GRUPO"]
    df_aula  = dataframe["AULA"]
    df_hora  = dataframe["HORARIO"]
    df_prof_id = dataframe["CÉDULA"]

    df_carrera = dataframe["VERSIÓN"]
    nivel = ''
    electiva = False
    
    for column_name, df_materia in dataframe.items():
        if column_name == "MATERIA":
            for i in range(len(df_materia)):
                if df_carrera[i] == "INGENIERÍA DE TELECOMUNICACIONES PRESENCIAL":
                    break
                if type(df_fac[i]) == str:
                    if df_fac[i][-1] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        nivel = df_fac[i][-1]
                    else:
                        nivel = 0
                        electiva = True

                if type(df_materia[i]) == str:
                    if type(df_fac[i+1]) == float:
                        courses.append([
                            str(df_fac[i]) + str(int(df_dep[i])) + str(df_mat[i]),
                            int(df_group[i]), df_materia[i], df_aula[i], df_aula[i+1], df_hora[i], df_hora[i+1]
                            ])
                        for_db.append([df_materia[i], int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                               int(df_mat[i]), 'T-P', int(nivel), getHoursLong(df_hora[i]),
                                               getHoursLong(df_hora[i+1]), 0, electiva, False,
                                               f'{df_hora[i]} {df_hora[i+1]}', df_prof_id[i], df_prof_id[i+1], df_aula[i], df_aula[i+1]])
                    else:
                        courses.append([
                            str(df_fac[i]) + str(int(df_dep[i])) + str(df_mat[i]),
                            int(df_group[i]), df_materia[i], df_aula[i], df_hora[i]
                            ])
                        for_db.append([df_materia[i], int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                               int(df_mat[i]), 'T', int(nivel), getHoursLong(df_hora[i]),
                                               0, 0, electiva, False, df_hora[i], df_prof_id[i],
                                               df_aula[i], 'NO'])
    print(for_db)

# days, _, duration = getClassSchedule("L8-10|M14-16")
# print(days, duration)
file_path = "data/A_PROGRAMACION.xlsx"
dataframe = read_excel_file(file_path)
getCleanData(dataframe)
