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
    days_hours_list = days_hours_string.split(" ")
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

def getCleanData(dataframe):
    df_fac   = dataframe["FAC"]
    df_dep   = dataframe["DEP"]
    df_mat   = dataframe["MAT"]
    df_group = dataframe["GRUPO"]
    df_aula  = dataframe["AULA"]
    df_hora  = dataframe["HORARIO"]
    
    for column_name, df_materia in dataframe.items():
        if column_name == "MATERIA":
            for i in range(100):
                if type(df_materia[i]) == str:
                    print(df_fac[i], int(df_dep[i]), df_mat[i], int(df_group[i]), df_materia[i], df_aula[i], df_hora[i])
                    print(df_fac[i], int(df_dep[i]), df_mat[i], int(df_group[i]), df_materia[i], df_aula[i+1], df_hora[i+1])


file_path = "data/A_PROGRAMACION.xlsx"
dataframe = read_excel_file(file_path)
getCleanData(dataframe)