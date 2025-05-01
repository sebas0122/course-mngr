import pandas as pd
import re

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
        letters = ["L", "M", "W", "J", "V", "S", "D"]
        if days_hours_string[1] in letters:
            x = days_hours_string[2:].split("-")
        else:
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
    es_dpt = False
    
    for column_name, df_materia in dataframe.items():
        if column_name == "MATERIA":
            for i in range(len(df_materia)):
                if df_carrera[i] == "INGENIERÍA DE TELECOMUNICACIONES PRESENCIAL":
                    break
                if type(df_fac[i]) == str:
                    if df_fac[i][-1] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        nivel = df_fac[i][-1]
                        if nivel == '4':
                            break
                    else:
                        nivel = 0
                        electiva = True
                    

                if type(df_materia[i]) == str:
                    materia_limpia = df_materia[i].replace('\n', '')
                    if int(df_dep[i]) == 47 or int(df_dep[i]) == 98:
                            es_dpt = True
                    if type(df_fac[i+1]) == float:
                        courses.append([
                            str(df_fac[i]) + str(int(df_dep[i])) + str(df_mat[i]),
                            int(df_group[i]), materia_limpia, df_aula[i], df_aula[i+1], df_hora[i], df_hora[i+1]
                            ])
                        #Teoria
                        for_db.append([materia_limpia, int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                        int(df_mat[i]), int(df_group[i]), 'T-P', False, int(nivel), getHoursLong(df_hora[i]),
                                        getHoursLong(df_hora[i+1]), 0, electiva, es_dpt,
                                        f'{df_hora[i]}', int(df_prof_id[i]), df_aula[i]])
                        #Práctica
                        for_db.append([materia_limpia, int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                        int(df_mat[i]), int(df_group[i]), 'T-P', True, int(nivel), getHoursLong(df_hora[i]),
                                        getHoursLong(df_hora[i+1]), 0, electiva, es_dpt,
                                        f'{df_hora[i+1]}', int(df_prof_id[i+1]), df_aula[i+1]])
                    else:
                        courses.append([
                            str(df_fac[i]) + str(int(df_dep[i])) + str(df_mat[i]),
                            int(df_group[i]), materia_limpia, df_aula[i], df_aula[i+1], df_hora[i], df_hora[i+1]
                            ])
                        #Teoria
                        for_db.append([materia_limpia, int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                        int(df_mat[i]), int(df_group[i]), 'T', False, int(nivel), getHoursLong(df_hora[i]),
                                        0, 0, electiva, es_dpt, f'{df_hora[i]}', int(df_prof_id[i]), df_aula[i]])
    print(for_db)
    return for_db

def write_db_to_file(template_file, out_db_file, data):
    with open(template_file, "r", encoding="utf-8") as file:
        template_content = file.read()

    # Extract everything between CREATE TABLE ... and the closing parenthesis
    table_body_match = re.search(r'CREATE TABLE.*?\((.*?)\);', template_content, re.DOTALL | re.IGNORECASE)

    if table_body_match:
        table_body = table_body_match.group(1)

        # Extract column names (lines that start with a name followed by a space and a data type)
        columns = []
        for line in table_body.strip().splitlines():
            line = line.strip().rstrip(',')
            if line and not line.upper().startswith(("PRIMARY", "FOREIGN", "UNIQUE", "CONSTRAINT")):
                col_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+', line)
                if col_match:
                    col_name = col_match.group(1)
                    if col_name.lower() != 'id':  # Skip 'id' if you want
                        columns.append(col_name)

        # Format as tuple string
        column_tuple = "(" + ", ".join(columns) + ")"
        print(column_tuple)
    else:
        print("No CREATE TABLE statement found.")

    # Regex to extract the table name
    match = re.search(r'CREATE TABLE\s+([a-zA-Z_][a-zA-Z0-9_]*)', template_content, re.IGNORECASE)

    if match:
        table_name = match.group(1)
        print(f"Table name: {table_name}")
    else:
        print("No table name found.")

    with open(out_db_file, "w", encoding="utf-8") as file:
        file.write(template_content)
        for cl in data:
            file.write("\ninsert into " + table_name + column_tuple + " values (")
            for item in cl:
                if isinstance(item, str):
                    item = f"'{item}'"
                elif isinstance(item, bool):
                    item = "true" if item else "false"
                elif item is None:
                    item = "null"
                else:
                    item = str(item)
                file.write(f"{item}, ")
            file.write(");\n")

file_path = "data/prog.xlsx"
dataframe = read_excel_file(file_path)
db_df = getCleanData(dataframe)
write_db_to_file("data/table_template.log", "data/db.log", db_df)