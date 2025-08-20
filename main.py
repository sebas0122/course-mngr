from tkinter import *
from tkinter import ttk
from dnd import *
from courses_functions import connectSQL, getClassesList, getProfessorsData, update_schedule_in_db

dataframe = connectSQL("materias") ##< Connect to the database and get the data

window = Tk() ##< Create a window

window.attributes('-fullscreen', True) ##< Set the window to fullscreen

screen_width = window.winfo_screenwidth() ##< Get the screen width
print("Screen width:", screen_width) ##< Print the screen width

screen_height = window.winfo_screenheight() ##< Get the screen height
print("Screen height:", screen_height) ##< Print the screen height

pixel = PhotoImage(width=1, height=1)

quit_button = Button(window, text="Quit", background="red", command=window.quit) ##< Create a quit button
quit_button.place(x=int(screen_width*(14/15)), y=0) ##< Set the position of the quit button

single_width = int(screen_width / 14) ##< Set the width of a single cell
single_height = int(screen_height / 25) ##< Set the height of a single cell

lab_displacement = int(2*single_width)-single_width ##< lab_displacement is to set the displacement of the labs cells in the grid (compared to the rooms). This is done to avoid overlapping with the rooms and avoid creating another xlimit list. The value is how many pixels is moved to the right.

# Add cells for hours
for hour in range(6, 22):
    label = Label(window,
                  image=pixel,
                  text=f"{hour}:00",
                  width=single_width-4,
                  height=single_height,
                  compound="center")
    if hour == 6:
        label.place(x=0, y=single_height*2) ##< Set the first label at 6:00
        ylimit.append(single_height*2)      ##< Add the position to the ylimit list
    else:
        label.place(x=0, y=single_height*2 + (hour - 6)*single_height) ##< Set the rest of the labels at 7:00 and above
        ylimit.append(single_height*2 + (hour - 6)*single_height)      ##< Add the position to the ylimit list

information_label = Label(window,
                          text="Course Information\n\nClick on a class or lab to see more information!",
                          font=("Arial", 16),
                          justify="left",
                          bg="#FFF1F1",
                          image=pixel,
                          height=screen_height - (ylimit[-1]+2*single_height),
                          width=screen_width,
                          compound="center") ##< Create a label for the test
information_label.place(x=0, y=ylimit[-1]+2*single_height) ##< Set the rest of the labels at 7:00 and above

# Add labels for days
for day in range(6):
    label = Label(window,
                  image=pixel,
                  text=days_es[day],
                  width=2*single_width-4,
                  height=single_height-4,
                  compound="center") ##< Create a label for each day
    if day == 0:
        label.place(x=single_width, y=0) ##< Set the label position
        xlimit.append(single_width)      ##< Add the position to the xlimit list
    else:
        label.place(x=(day)*int(2*single_width)+single_width, y=0)
        xlimit.append((day)*int(2*single_width)+single_width)      ##< Add the position to the xlimit list

# Add rooms and labs in use each day each hour by semester
for xl in xlimit:
    room = Label(window,
                 image=pixel,
                 text="Teoría",
                 width=single_width-4,
                 height=single_height-4,
                 compound="center") ##< Create a label for the room
    room.place(x=xl, y=single_height) ##< Set the label position
    
    lab = Label(window,
                image=pixel,
                text="Lab",
                width=single_width-4,
                height=single_height-4,
                compound="center") ##< Create a label for the lab
    lab.place(x=xl+lab_displacement, y=single_height) ##< Set the label position

# Add separator lines
for hour in range(6, 23):    
    # Add a separator line for each hour
    separator = ttk.Separator(window, orient='horizontal')
    if hour < 22:
        separator.place(x=0, y=ylimit[hour-6], width=single_width+6*(2*single_width)) ##< Set the position of the separator line
    else:
        separator.place(x=0, y=ylimit[hour-7]+single_height, width=single_width+6*(2*single_width))

for xl in xlimit:
    # Add a vertical separator line for each room
    separator = ttk.Separator(window, orient='vertical')
    separator.place(x=xl, y=single_height, height=(2+(21-6))*single_height) ##< Set the position of the separator line
    # Add a vertical separator line for each lab
    separator = ttk.Separator(window, orient='vertical')
    separator.place(x=xl+lab_displacement, y=single_height, height=(2+(21-6))*single_height) ##< Set the position of the separator line
separator = ttk.Separator(window, orient='vertical')
separator.place(x=xlimit[-1]+single_width+lab_displacement, y=single_height, height=(2+(21-6))*single_height) ##< Set the position of the separator line

colors = ["#B89E97", "#4ECDC4", "#BCBD8B", "#FF9770", "#6EA4BF", "#385F71", "#D6D84F"] ##< Set the colors for the classes and labs
colors_idx = 0 ##< Initialize the index for the colors
class_colors_dict = {} ##< Initialize the dictionary for the class colors

# print(xlimit) ##< Print the xlimit list
# print(ylimit)

## add_classes_labs function
# This function adds classes and labs to the schedule. It takes the following parameters:
# - classes: a list of classes for each day
# - labs: a list of labs for each day
# Returns:
# - labels_ids: a list of labels ids for the classes and labs added to the schedule
def add_classes_labs(classes, labs, cl_information_label, lb_information_label):
    global colors_idx, class_colors_dict, screen_width, screen_height, single_width, single_height, lab_displacement
    labels_ids = [] ##< Initialize the list of labels ids
    # Add classes (rooms) to schedule
    i = 0 ##< Initialize the index for xlimit
    for day in classes: ##< Iterate over the classes
        for cl in day:

            temp = cl.split("_") ##< Split the string to get the class name and hours
            c_name = temp[0].split("\n")[0]
            c_st_hour = int(temp[1])
            c_duration = int(temp[2])
            c_room = temp[3]

            if c_name not in class_colors_dict: ##< Check if the class is not already in the dictionary
                class_colors_dict[c_name] = colors[colors_idx] ##< Add the class to the dictionary with the color
                colors_idx += 1 ##< Increment the index for the colors

            dnd_label(window=window,
                        image=pixel,
                        geometry_width=screen_width,
                        geometry_height=screen_height,
                        lab_disp=0,
                        text=temp[0],
                        bg_color=class_colors_dict[c_name],
                        w=single_width-4,
                        h=(c_duration*single_height)-4,
                        posx=xlimit[i],
                        posy=ylimit[c_st_hour-6],
                        hours=c_duration,
                        type="class",
                        room=c_room,
                        info_label=information_label,
                        cl_info=cl_information_label) ##< Create the drag&drop label for the class

            labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
        i+=1 ##< Increment the index for xlimit by 1

    # Add labs to schedule
    i = 0 ##< Initialize the index for xlimit
    for day in labs: ##< Iterate over the labs
        for cl in day:

            temp = cl.split("_") ##< Split the string to get the lab name and hours
            c_name = temp[0].split("\n")[0]
            c_st_hour = int(temp[1])
            c_duration = int(temp[2])
            c_room = temp[3]

            dnd_label(window=window,
                        image=pixel,
                        geometry_width=screen_width,
                        geometry_height=screen_height,
                        lab_disp=lab_displacement,
                        text=temp[0],
                        bg_color=class_colors_dict[c_name],
                        w=single_width-4,
                        h=(c_duration*single_height)-4,
                        posx=xlimit[i]+lab_displacement,
                        posy=ylimit[c_st_hour-6],
                        hours=c_duration,
                        type="lab",
                        room=c_room,
                        info_label=information_label,
                        cl_info=lb_information_label) ##< Create the drag&drop label for the lab

            labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
        i+=1 ##< Increment the index for xlimit by 1

    return labels_ids ##< Return the list of labels ids

c, l, c_info, l_info = getClassesList(dataframe, 1) ##< Get the classes and labs for level 1
lbs_ids = add_classes_labs(c, l, c_info, l_info) ##< Call the function to add classes and labs to the schedule

# Add dropdown menu for level selection

## change_level function
# This function is called when the user selects a level from the dropdown menu. It updates the schedule with the classes and labs for the selected level.
# It takes no parameters and returns nothing because it modifies the global variable lbs_ids.
def change_level():
    global lbs_ids, c_info, l_info, colors_idx, class_colors_dict
    colors_idx = 0 ##< Reset the index for the colors
    class_colors_dict = {} ##< Reset the dictionary for the class colors

    dataframe = connectSQL("materias") ##< Connect to the database and get the data

    # Destroy all dnd_labels
    for widget in window.winfo_children():
        if len(lbs_ids) == 0:
            break
        if isinstance(widget, Label):
            if widget == lbs_ids[0]:
                lbs_ids.remove(widget) ##< Remove the label id from the list
                widget.destroy()

    # Add classes and labs to the schedule based on the selected level
    if opt.get() == "Nivel 1":
        c, l, c_info, l_info = getClassesList(dataframe, 1) ##< Call the function to add classes and labs to the schedule
    elif opt.get() == "Nivel 2":
        c, l, c_info, l_info = getClassesList(dataframe, 2) ##< Call the function to add classes and labs to the schedule
    elif opt.get() == "Nivel 3":
        c, l, c_info, l_info = getClassesList(dataframe, 3)
    elif opt.get() == "Nivel 4":
        c, l, c_info, l_info = getClassesList(dataframe, 4)
    elif opt.get() == "Nivel 5":
        c, l, c_info, l_info = getClassesList(dataframe, 5)
    elif opt.get() == "Nivel 6":
        c, l, c_info, l_info = getClassesList(dataframe, 6)
    elif opt.get() == "Nivel 7":
        c, l, c_info, l_info = getClassesList(dataframe, 7)
    elif opt.get() == "Nivel 8":
        c, l, c_info, l_info = getClassesList(dataframe, 8)
    elif opt.get() == "Nivel 9":
        c, l, c_info, l_info = getClassesList(dataframe, 9)
    lbs_ids = add_classes_labs(c, l, c_info, l_info)

# Dropdown options
level = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5", "Nivel 6", "Nivel 7", "Nivel 8", "Nivel 9"] 

# Selected option variable  
opt = StringVar(value="Nivel 1")

# Dropdown menu  
dd_menu = OptionMenu(window, opt, *level)
dd_menu.place(x=int(screen_width*(14/15)), y=single_height*2) ##< Set the position of the quit button

# Button to update label  
dd_button = Button(window, text="Aceptar", command=change_level, background="lightblue")
dd_button.place(x=int(screen_width*(14/15)), y=single_height*4) ##< Set the position of the quit button

def open_add_class_window():
    add_win = Toplevel(window)
    add_win.title("Add Class")
    add_win.geometry("400x300")

    # --- Form Fields ---
    Label(add_win, text="Nombre:").grid(row=0, column=0, sticky="e")
    name_entry = Entry(add_win)
    name_entry.grid(row=0, column=1)

    Label(add_win, text="Código:").grid(row=1, column=0, sticky="e")
    code_entry = Entry(add_win)
    code_entry.grid(row=1, column=1)

    Label(add_win, text="ID del Profesor:").grid(row=2, column=0, sticky="e")
    prof_entry = Entry(add_win)
    prof_entry.grid(row=2, column=1)

    Label(add_win, text="Aula:").grid(row=3, column=0, sticky="e")
    room_entry = Entry(add_win)
    room_entry.grid(row=3, column=1)

    Label(add_win, text="Día:").grid(row=4, column=0, sticky="e")
    day_var = StringVar(value="Lunes")
    OptionMenu(add_win, day_var, "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado").grid(row=4, column=1)

    Label(add_win, text="Hora de Inicio:").grid(row=5, column=0, sticky="e")
    start_entry = Entry(add_win)
    start_entry.grid(row=5, column=1)

    Label(add_win, text="Duración:").grid(row=6, column=0, sticky="e")
    duration_entry = Entry(add_win)
    duration_entry.grid(row=6, column=1)

    Label(add_win, text="Tipo:").grid(row=7, column=0, sticky="e")
    type_var = StringVar(value="Teoría")
    OptionMenu(add_win, type_var, "Teoría", "Laboratorio").grid(row=7, column=1)

    Label(add_win, text="Grupo(s)").grid(row=8, column=0, sticky="e")
    group_entry = Entry(add_win)
    group_entry.grid(row=8, column=1)

    # --- Save Handler ---
    def save_class():
        name = name_entry.get()
        code = code_entry.get()
        professor = int(prof_entry.get())
        room = room_entry.get()
        day = day_var.get()
        start_hour = int(start_entry.get())
        duration = int(duration_entry.get())
        is_lab = (type_var.get() == "Laboratorio")
        group = group_entry.get()

        # Update data dictionary
        key = f"{name}_{start_hour}_{duration}_{day}"
        info_dict = {
            "nombre": name,
            "codigo": code,
            "profesor": [professor],
            "grupo": group.split(", ") if ", " in group else [group],
            "aula": room
        }

        if opt.get() == "Nivel 1":
            c, l, c_info, l_info = getClassesList(dataframe, 1) ##< Call the function to add classes and labs to the schedule
        elif opt.get() == "Nivel 2":
            c, l, c_info, l_info = getClassesList(dataframe, 2) ##< Call the function to add classes and labs to the schedule
        elif opt.get() == "Nivel 3":
            c, l, c_info, l_info = getClassesList(dataframe, 3)
        elif opt.get() == "Nivel 4":
            c, l, c_info, l_info = getClassesList(dataframe, 4)
        elif opt.get() == "Nivel 5":
            c, l, c_info, l_info = getClassesList(dataframe, 5)
        elif opt.get() == "Nivel 6":
            c, l, c_info, l_info = getClassesList(dataframe, 6)
        elif opt.get() == "Nivel 7":
            c, l, c_info, l_info = getClassesList(dataframe, 7)
        elif opt.get() == "Nivel 8":
            c, l, c_info, l_info = getClassesList(dataframe, 8)
        elif opt.get() == "Nivel 9":
            c, l, c_info, l_info = getClassesList(dataframe, 9)

        if is_lab:
            l_info[key] = info_dict
            print("Labs info:", l_info)
        else:
            c_info[key] = info_dict
            print("Classes info:", c_info)

        # Add to UI immediately
        bg_color = class_colors_dict.get(name)
        if not bg_color:
            global colors_idx
            class_colors_dict[name] = colors[colors_idx]
            bg_color = class_colors_dict[name]
            colors_idx += 1

        dnd_label(window=window,
                  image=pixel,
                  geometry_width=screen_width,
                  geometry_height=screen_height,
                  lab_disp=lab_displacement if is_lab else 0,
                  text=name,
                  bg_color=bg_color,
                  w=single_width-4,
                  h=(duration * single_height) - 4,
                  posx=xlimit[days_es.index(day)] + (lab_displacement if is_lab else 0),
                  posy=ylimit[start_hour - 6],
                  hours=duration,
                  type="lab" if is_lab else "class",
                  info_label=information_label,
                  cl_info=l_info if is_lab else c_info) ##< Create the drag&drop label for the class or lab

        add_win.destroy()

    Button(add_win, text="Guardar", command=save_class, bg="lightgreen").grid(row=9, column=0, columnspan=2)

# Button for adding a new class
add_button = Button(window, text="Añadir\nClase", command=open_add_class_window, background="lightyellow")
add_button.place(x=int(screen_width*(14/15)), y=single_height*8) ##< Set the position of the quit button

def update_database():
    print(c_info)
    update_schedule_in_db(c_info, False) ##< Function to update the database with the current schedule
    update_schedule_in_db(l_info, True) ##< Function to update the database with the current schedule
# Button for updating database
update_button = Button(window, text="Guardar\nCambios", command=update_database, background="lightgreen") ##< Create a button to update the database
update_button.place(x=int(screen_width*(14/15)), y=single_height*10)

window.mainloop() ##< Start the main loop of the window