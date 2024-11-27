import pandas as pd

def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
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

def getWeekSchedule(dataframe, semester):
    cols_to_remove = [i for i in dataframe.columns if i != "DEP" and i != "CURSOS" and i != "NIVEL" and i != "CUPO" and i != "HORARIO"]

    dataframe = dataframe.drop(columns=cols_to_remove)
    dataframe = dataframe[dataframe['NIVEL'] == str(semester)]
    dataframe = dataframe[dataframe['DEP'] == 98]
    dataframe = dataframe[dataframe['CUPO'].isnull() == False]

    dataframe['HORARIO'] = dataframe['HORARIO'].apply(getClassSchedule)

    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    classes = [[],[],[],[],[],[]]

    for index, row in dataframe.iterrows():
        days, start_hour, class_duration = row['HORARIO']
        for day in days:
            i = week_days.index(day)
            if f"{start_hour[0]}_{row['CURSOS']}_{class_duration[0]}" not in classes[i] and class_duration[0] == 2:
                classes[i].append(f"{start_hour[0]}_{row['CURSOS']}_{class_duration[0]}")

    # Target range and the sublist to process
    start = 6
    end = 22
    for i in range(len(classes)):
        sublist = classes[i]

        if sublist == []:
            classes[i] = [f"BLANK_{end - start}"]
            continue

        # Parse and sort the sublist
        sorted_sublist = sorted(sublist, key=lambda x: int(x.split('_')[0]))

        # Initialize the result list and the current position tracker
        result = []
        current_position = start

        # Fill in the gaps
        for item in sorted_sublist:
            item_start, item_label, item_duration = item.split('_')
            item_start = int(item_start)
            item_duration = int(item_duration)

            # Add blanks if there's a gap
            if item_start > current_position:
                result.append(f"BLANK_{item_start - current_position}")
                current_position = item_start

            # Add the current item and update the current position
            result.append(f"{item_label}_{item_duration}")
            current_position += item_duration

        # Fill in any remaining blanks
        if current_position < end:
            result.append(f"BLANK_{end - current_position}")

        # Replace the original sublist with the updated one
        classes[i] = result

    return classes


# Example usage
file_path = "data/programacion.xlsx"
dataframe = read_excel_file(file_path)
df = getWeekSchedule(dataframe, 5)
print(df)