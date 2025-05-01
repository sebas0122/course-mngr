import pandas as pd
import re

def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="PROGRAMACION_2025_1")
        print("Excel file read successfully!")
        return df
    except Exception as e:
        print(f"An error occurred: {e}")

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
                class_duration.append(int(sch[2:].split("-")[1]) - int(sch[2:].split("-")[0])) ##< Add the class duration to the list

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

## getCleanData function
# This function takes a DataFrame and processes it to extract relevant information for the database.
# It iterates through the DataFrame and cleans the data, creating a list of courses and a list for the database.
# It takes the following parameter:
# - dataframe: a DataFrame containing the data to be processed
# Returns:
# - for_db: a list of lists containing the cleaned data for the database
def getCleanData(dataframe):

    courses = [] ##< Initialize the list of courses
    for_db = []  ##< Initialize the list for the database format
    
    df_fac   = dataframe["FAC"] ##< Get the FAC column from the dataframe
    df_dep   = dataframe["DEP"] ##< Get the DEP column from the dataframe
    df_ide   = dataframe["IDE"] ##< Get the IDE column from the dataframe
    df_mat   = dataframe["MAT"] ##< Get the MAT column from the dataframe
    df_group = dataframe["GRUPO"] ##< Get the GRUPO column from the dataframe
    df_aula  = dataframe["AULA"]  ##< Get the AULA column from the dataframe
    df_hora  = dataframe["HORARIO"] ##< Get the HORARIO column from the dataframe
    df_prof_id = dataframe["CÉDULA"] ##< Get the CÉDULA column from the dataframe
    df_cupo = dataframe["CUPO"] ##< Get the CUPO column from the dataframe

    df_carrera = dataframe["VERSIÓN"] ##< Get the VERSIÓN column from the dataframe
    nivel = '' ##< Initialize the nivel variable, this indicates the semester level
    electiva = False ##< Initialize the electiva variable, this indicates if the course is elective
    es_dpt = False   ##< Initialize the es_dpt variable, this indicates if the course is from the department
    
    for column_name, df_materia in dataframe.items(): ##< Iterate over the columns in the dataframe
        if column_name == "MATERIA": ##< Check if the column name is MATERIA
            for i in range(len(df_materia)):
                if df_carrera[i] == "INGENIERÍA DE TELECOMUNICACIONES PRESENCIAL":
                    break
                if type(df_fac[i]) == str: ##< Check if the value in the FAC column is a string
                    if df_fac[i][-1] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        nivel = df_fac[i][-1] ##< Get the last character of the FAC (because extracted from title "NIVEL N") column value as the nivel
                        # if nivel == '9':
                        #     break
                    else:
                        nivel = 0 ##< Set nivel to 0 if the last character is not a number
                        electiva = True ##< Set electiva to True if the last character is not a number
                    

                if type(df_materia[i]) == str: ##< Check if the value in the MATERIA column is a string
                    if df_cupo[i] == "0": ##< Check if the value in the CUPO column is 0
                        continue ##< Skip the iteration if the value in the CUPO column is 0, means the course is not available
                    materia_limpia = df_materia[i].replace('\n', '') ##< Clean the MATERIA column value by removing new line characters
                    print(materia_limpia)
                    if int(df_dep[i]) == 47 or int(df_dep[i]) == 98: ##< Check if the value in the DEP column is 47 or 98, indicating a specific department
                        es_dpt = True
                    if "|" in str(df_prof_id[i]): ##< Check if the value in the CÉDULA column contains "|", indicating multiple professors
                        prof_id     = int(df_prof_id[i].split("|")[0]) ##< Get the first part of the CÉDULA column value as the prof_id
                        sec_prof_id = int(df_prof_id[i].split("|")[1]) ##< Get the second part of the CÉDULA column value as the sec_prof_id
                    else:
                        prof_id     = int(df_prof_id[i]) ##< Get the CÉDULA column value as the prof_id
                        sec_prof_id = None ##< Set sec_prof_id to None if there is no second part in the CÉDULA column value
                        if type(df_fac[i+1]) == float: ##< Check if the next value in the FAC column is a float, indicating a lab
                            try:
                                lab_prof_id = int(df_prof_id[i+1]) ##< Get the next CÉDULA column value as the lab_prof_id
                            except:
                                lab_prof_id = int(df_prof_id[i]) ##< Set lab_prof_id to the current CÉDULA column value if there is an error in conversion
                    
                    if type(df_fac[i+1]) == float: ##< Check if the next value in the FAC column is a float, indicating a lab
                        courses.append([
                            str(df_fac[i]) + str(int(df_dep[i])) + str(df_mat[i]),
                            int(df_group[i]), materia_limpia, df_aula[i], df_aula[i+1], df_hora[i], df_hora[i+1]
                            ])
                        # Append the course theory information to the courses list
                        for_db.append([materia_limpia, int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                        int(df_mat[i]), int(df_group[i]), 'T-P', False, int(nivel), getHoursLong(df_hora[i]),
                                        getHoursLong(df_hora[i+1]), 0, electiva, es_dpt,
                                        f'{df_hora[i]}', prof_id, sec_prof_id, str(df_aula[i])])
                        # Append the course lab information to the courses list
                        for_db.append([materia_limpia, int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                        int(df_mat[i]), int(df_group[i]), 'T-P', True, int(nivel), getHoursLong(df_hora[i]),
                                        getHoursLong(df_hora[i+1]), 0, electiva, es_dpt,
                                        f'{df_hora[i+1]}', lab_prof_id, sec_prof_id, str(df_aula[i+1])])
                    else: ##< If the next value in the FAC column is not a float, indicating a theory course
                        courses.append([
                            str(df_fac[i]) + str(int(df_dep[i])) + str(df_mat[i]),
                            int(df_group[i]), materia_limpia, df_aula[i], df_aula[i+1], df_hora[i], df_hora[i+1]
                            ])
                        # Append the course theory information to the courses list
                        for_db.append([materia_limpia, int(df_fac[i]), int(df_dep[i]), df_ide[i],
                                        int(df_mat[i]), int(df_group[i]), 'T', False, int(nivel), getHoursLong(df_hora[i]),
                                        0, 0, electiva, es_dpt, f'{df_hora[i]}', prof_id, sec_prof_id, str(df_aula[i])])
    print(for_db)
    return for_db

## write_db_to_file function
# This function takes a template file, an output database file, and data (in for_db format, returned by getCleanData function) to write to the database.
# It reads the template file, extracts the table name and column names, and writes the data to the output file in SQL format.
# It takes the following parameters:
# - template_file: the path to the template file
# - out_db_file: the path to the output database file
# - data: the data to be written to the database
def write_db_to_file(template_file, out_db_file, data):
    # Read the template file and extract the table name and column names
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

    # Write the data to the output database file
    with open(out_db_file, "w", encoding="utf-8") as file:
        file.write(template_content) ##< Write the template content to the output file
        file.write("\n\n") ##< Add a new line after the template content
        for cl in data: ##< Iterate over the data
            file.write("insert into " + table_name + " " + column_tuple + " values (") ##< Write the insert statement with the table name and column names
            for item in cl: ##< Iterate over the items in the data

                # Convert the item to a representation based on SQL format
                if isinstance(item, str):
                    item_write = f"'{item}'"
                elif isinstance(item, bool):
                    item_write = "true" if item else "false"
                elif item is None:
                    item_write = "null"
                else:
                    item_write = str(item)
                
                # Check if it's the last item in the list
                if item == cl[-1]:
                    file.write(f"{item_write}")
                else:
                    file.write(f"{item_write}, ")

            # Close the insert statement
            file.write(");\n")

file_path = "data/prog.xlsx"
dataframe = read_excel_file(file_path)
db_df = getCleanData(dataframe)
write_db_to_file("data/table_template.log", "data/db.log", db_df)