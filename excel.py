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
            print("L" in days_dict)
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

# Example usage
file_path = "data/info.xlsx"
dataframe = read_excel_file(file_path)
print(dataframe.head())
print(dataframe["Horario"][0])
print(getClassSchedule(dataframe["Horario"][0]))