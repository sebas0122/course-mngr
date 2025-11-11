from tkinter import *
from tkinter import ttk
import customtkinter as ctk

from dnd import *
from courses_functions import connectSQL, retrieveDBTable, getClassesList, getProfessorsData, update_schedule_in_db, delete_class_in_db

supabase_instance = connectSQL() ##< Connect to the database
dataframe = retrieveDBTable(supabase_instance, "materias") ##< Connect to the database and get the data

ctk.set_appearance_mode("Light") ##< Set the appearance mode to light
ctk.set_default_color_theme("blue")

window = Tk() ##< Create a window

window.attributes('-fullscreen', True) ##< Set the window to fullscreen

screen_width = window.winfo_screenwidth() ##< Get the screen width

screen_height = window.winfo_screenheight() ##< Get the screen height

pixel = PhotoImage(width=1, height=1)

quit_button = Button(window, text="Quit", background="red", command=window.quit) ##< Create a quit button
quit_button.place(x=int(screen_width*(14/15)), y=0) ##< Set the position of the quit button

single_width = int(screen_width / 14) ##< Set the width of a single cell
single_height = int(screen_height / 22) ##< Set the height of a single cell

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
                          font=("Arial", 12),
                          justify="left",
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

colors = ["#F2DFD7", "#DBA159", "#6A8D92", "#80B192", "#A1E887", "#385F71", "#FFC482"] ##< Set the colors for the classes and labs
colors_idx = 0 ##< Initialize the index for the colors
class_colors_dict = {} ##< Initialize the dictionary for the class colors

class_edit = {"key": None} 
classes_edited_keys = [] ##< Initialize the list of classes and labs edited keys
labs_edited_keys = [] ##< Initialize the list of classes and labs edited keys
deleted_keys = [] ##< Initialize the list of classes and labs deleted keys
## add_classes_labs function
# This function adds classes and labs to the schedule. It takes the following parameters:
# - classes: a list of classes for each day
# - labs: a list of labs for each day
# Returns:
# - labels_ids: a list of labels ids for the classes and labs added to the schedule
def add_classes_labs(classes, labs, cl_information_label, lb_information_label, professors_information):
    global colors_idx, class_colors_dict, screen_width, screen_height, single_width, single_height, lab_displacement, class_edit
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
                        cl_info=cl_information_label,
                        proffs_info=professors_information,
                        cell_to_edit=class_edit,
                        c_edited=classes_edited_keys) ##< Create the drag&drop label for the class

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
                        cl_info=lb_information_label,
                        proffs_info=professors_information,
                        cell_to_edit=class_edit,
                        c_edited=labs_edited_keys) ##< Create the drag&drop label for the lab

            labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
        i+=1 ##< Increment the index for xlimit by 1

    return labels_ids ##< Return the list of labels ids

c, l, c_info, l_info = getClassesList(dataframe, 1) ##< Get the classes and labs for level 1
p_info = getProfessorsData(supabase_instance)
lbs_ids = add_classes_labs(c, l, c_info, l_info, p_info) ##< Call the function to add classes and labs to the schedule

# Add dropdown menu for level selection

## change_level function
# This function is called when the user selects a level from the dropdown menu. It updates the schedule with the classes and labs for the selected level.
# It takes no parameters and returns nothing because it modifies the global variable lbs_ids.
def change_level():
    global lbs_ids, c_info, l_info, colors_idx, class_colors_dict, supabase_instance
    colors_idx = 0 ##< Reset the index for the colors
    class_colors_dict = {} ##< Reset the dictionary for the class colors

    dataframe = retrieveDBTable(supabase_instance, "materias") ##< Connect to the database and get the data

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
    p_info = getProfessorsData(supabase_instance)
    lbs_ids = add_classes_labs(c, l, c_info, l_info, p_info)

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
    add_win.geometry("400x450")

    # --- Form Fields ---
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre")
    name_entry.pack(pady=5)

    # --- Row for code entries ---
    row_code_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_frame.pack(pady=5)

    fac_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Facultad", width=70)
    fac_entry.pack(padx=5, side=LEFT)

    dep_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Dependencia", width=90)
    dep_entry.pack(padx=5, side=LEFT)

    mat_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Materia", width=60)
    mat_entry.pack(padx=5, side=LEFT)

    # small mapping for codes -> names (add more codes as needed)
    _fac_map = {"25": "Ingeniería"}
    _dep_map = {"98": "Electrónica"}

    # --- Row for code labels ---
    row_code_labels_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_labels_frame.pack(pady=2)

    fac_label = ctk.CTkLabel(row_code_labels_frame, text="<Facultad>")
    fac_label.pack(padx=5, side=LEFT)

    dep_label = ctk.CTkLabel(row_code_labels_frame, text="<Dependencia>")
    dep_label.pack(padx=5, side=LEFT)

    def _update_code_labels(event=None):
        f = fac_entry.get().strip()
        d = dep_entry.get().strip()
        fac_label.configure(text=_fac_map.get(f, "<Facultad>"))
        dep_label.configure(text=_dep_map.get(d, "<Dependencia>"))

    # bind updates so label changes while typing or after leaving the field
    fac_entry.bind("<KeyRelease>", _update_code_labels)
    fac_entry.bind("<FocusOut>", _update_code_labels)
    dep_entry.bind("<KeyRelease>", _update_code_labels)
    dep_entry.bind("<FocusOut>", _update_code_labels)

    # --- Row for professor ID and name ---
    row_prof_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_prof_frame.pack(pady=5)

    prof_entry = ctk.CTkEntry(row_prof_frame, placeholder_text="ID del Profesor")
    prof_entry.pack(padx=2, side=LEFT)

    p_info = getProfessorsData(supabase_instance)
    print(p_info)
    # build a safe id->name mapping for different return shapes from getProfessorsData
    def _build_prof_map(prof_data):
        mapping = {}
        if isinstance(prof_data, dict):
            for k, v in prof_data.items():
                mapping[str(k)] = v if isinstance(v, str) else (v.get('name') if isinstance(v, dict) else str(v))
            return mapping
        try:
            for prof in prof_data:
                if isinstance(prof, dict) and 'id' in prof and 'name' in prof:
                    mapping[str(prof['id'])] = prof['name']
                elif isinstance(prof, (list, tuple)) and len(prof) >= 2:
                    mapping[str(prof[0])] = prof[1]
                elif isinstance(prof, str):
                    if ':' in prof:
                        id_, name = prof.split(':', 1)
                        mapping[id_.strip()] = name.strip()
            return mapping
        except TypeError:
            return {}

    _p_map = _build_prof_map(p_info)
    print(_p_map)
    prof_label = ctk.CTkLabel(row_prof_frame, text="<Nombre del profesor>")
    prof_label.pack(padx=2, side=LEFT)

    def _update_prof_label(event=None):
        p = prof_entry.get().strip()
        prof_label.configure(text=_p_map.get(p, "<Nombre del profesor>"))

    # bind updates so label changes while typing or after leaving the field
    prof_entry.bind("<KeyRelease>", _update_prof_label)
    prof_entry.bind("<FocusOut>", _update_prof_label)

    room_entry = ctk.CTkEntry(add_win, placeholder_text="Aula")
    room_entry.pack(pady=5)

    day_var = ctk.StringVar(value="Día")
    ctk.CTkOptionMenu(add_win,
                      values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
                      variable=day_var).pack(pady=5)

    start_entry = ctk.CTkEntry(add_win, placeholder_text="Hora de Inicio")
    start_entry.pack(pady=5)

    duration_entry = ctk.CTkEntry(add_win, placeholder_text="Duración")
    duration_entry.pack(pady=5)

    type_var = ctk.StringVar(value="Tipo")
    ctk.CTkOptionMenu(add_win,
                      values=["Teoría", "Laboratorio"],
                      variable=type_var).pack(pady=5)

    group_entry = ctk.CTkEntry(add_win, placeholder_text="Grupo(s)")
    group_entry.pack(pady=5)

    # --- Save Handler ---
    def save_class():
        global p_info, lbs_ids
        name = name_entry.get()
        fac = fac_entry.get()
        dep = dep_entry.get()
        mat = mat_entry.get()
        professor = int(prof_entry.get())
        room = room_entry.get()
        day = day_var.get()
        start_hour = int(start_entry.get())
        duration = int(duration_entry.get())
        is_lab = (type_var.get() == "Laboratorio")
        group = group_entry.get()

        # Update data dictionary
        key = f"{name}_{start_hour}_{duration}_{day}_{room}"
        info_dict = {
            "id": [0],
            "nivel": int(opt.get().split(" ")[1]),
            "nombre": name,
            "facultad": fac,
            "dependencia": dep,
            "materia": mat,
            "codigo": f"{fac}{dep}{mat}",
            "profesor": [professor],
            "grupo": [int(g.strip()) for g in group.split(",")] if "," in group else [int(group)],
            "aula": room
        }

        if is_lab:
            l_info[key] = info_dict
            labs_edited_keys.append(key)
        else:
            c_info[key] = info_dict
            classes_edited_keys.append(key)

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
                  text=f"{name}\n{info_dict['grupo']}",
                  bg_color=bg_color,
                  w=single_width-4,
                  h=(duration * single_height) - 4,
                  posx=xlimit[days_es.index(day)] + (lab_displacement if is_lab else 0),
                  posy=ylimit[start_hour - 6],
                  hours=duration,
                  type="lab" if is_lab else "class",
                  room=room,
                  info_label=information_label,
                  cl_info=l_info if is_lab else c_info,
                  proffs_info=p_info,
                  cell_to_edit=class_edit,
                  c_edited=labs_edited_keys if is_lab else classes_edited_keys) ##< Create the drag&drop label for the class or lab
        
        lbs_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list

        add_win.destroy()

    ctk.CTkButton(add_win, text="Guardar", command=save_class).pack(pady=20)

# Button for adding a new class
add_button = Button(window, text="Añadir\nClase", command=open_add_class_window, background="lightyellow")
add_button.place(x=int(screen_width*(14/15)), y=single_height*8) ##< Set the position of the quit button

def update_database():
    update_schedule_in_db(supabase_instance, c_info, classes_edited_keys, False) ##< Function to update the database with the current schedule
    update_schedule_in_db(supabase_instance, l_info, labs_edited_keys, True) ##< Function to update the database with the current schedule
    delete_class_in_db(supabase_instance, deleted_keys) ##< Function to delete the selected classes and labs from the database
    classes_edited_keys.clear() ##< Clear the list of classes edited keys
    labs_edited_keys.clear() ##< Clear the list of labs edited keys
    deleted_keys.clear() ##< Clear the list of deleted keys
    change_level() ##< Refresh the schedule display
# Button for updating database
update_button = Button(window, text="Guardar\nCambios", command=update_database, background="lightgreen") ##< Create a button to update the database
update_button.place(x=int(screen_width*(14/15)), y=single_height*10)

def open_edit_class_window():
    add_win = Toplevel(window)
    add_win.title("Edit Class")
    add_win.geometry("400x500")

    # --- Form Fields ---
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre")
    name_entry.pack(pady=5)
    name_entry.insert(0, c_info[class_edit['key']]['nombre'] if class_edit['key'] in c_info else l_info[class_edit['key']]['nombre'])

     # --- Row for code entries ---
    row_code_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_frame.pack(pady=5)

    fac_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Facultad", width=70)
    fac_entry.pack(padx=5, side=LEFT)
    fac_entry.insert(0, c_info[class_edit['key']]['facultad'] if class_edit['key'] in c_info else l_info[class_edit['key']]['facultad'])
    fac_entry.configure(state="disabled")

    dep_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Dependencia", width=90)
    dep_entry.pack(padx=5, side=LEFT)
    dep_entry.insert(0, c_info[class_edit['key']]['dependencia'] if class_edit['key'] in c_info else l_info[class_edit['key']]['dependencia'])
    dep_entry.configure(state="disabled")   

    mat_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Materia", width=60)
    mat_entry.pack(padx=5, side=LEFT)
    mat_entry.insert(0, c_info[class_edit['key']]['materia'] if class_edit['key'] in c_info else l_info[class_edit['key']]['materia'])
    mat_entry.configure(state="disabled")

    # mapping for edit window (same as above; extend as needed)
    _fac_map = {"25": "Ingeniería"}
    _dep_map = {"98": "Electrónica"}

    # --- Row for code labels ---
    row_code_labels_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_labels_frame.pack(pady=2)

    fac_label = ctk.CTkLabel(row_code_labels_frame, text="<Facultad>")
    fac_label.pack(padx=10, side=LEFT)

    dep_label = ctk.CTkLabel(row_code_labels_frame, text="<Dependencia>")
    dep_label.pack(padx=5, side=LEFT)

    def _update_code_labels_edit(event=None):
        f = fac_entry.get().strip()
        d = dep_entry.get().strip()
        fac_label.configure(text=_fac_map.get(f, "<Facultad>"))
        dep_label.configure(text=_dep_map.get(d, "<Dependencia>"))

    # entries are disabled in edit window; just set labels once
    _update_code_labels_edit()

    # --- Row for professor ID and name ---
    row_prof_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_prof_frame.pack(pady=5)

    prof_entry = ctk.CTkEntry(row_prof_frame, placeholder_text="ID del Profesor")
    prof_entry.pack(padx=2, side=LEFT)
    prof_entry.insert(0, ", ".join(map(str, c_info[class_edit['key']]['profesor'])) if class_edit['key'] in c_info else ", ".join(map(str, l_info[class_edit['key']]['profesor'])))

    prof_label = ctk.CTkLabel(row_prof_frame, text="<Nombre del profesor>")
    prof_label.pack(padx=2, side=LEFT)

    room_entry = ctk.CTkEntry(add_win, placeholder_text="Aula")
    room_entry.pack(pady=5)
    room_entry.insert(0, c_info[class_edit['key']]['aula'] if class_edit['key'] in c_info else l_info[class_edit['key']]['aula'])

    day_var = ctk.StringVar(value=class_edit['key'].split("_")[3])
    ctk.CTkOptionMenu(add_win,
                      values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
                      variable=day_var, state="disabled").pack(pady=5)

    start_entry = ctk.CTkEntry(add_win, placeholder_text="Hora de Inicio")
    start_entry.pack(pady=5)
    start_entry.insert(0, class_edit['key'].split("_")[1])
    start_entry.configure(state="disabled")

    duration_entry = ctk.CTkEntry(add_win, placeholder_text="Duración")
    duration_entry.pack(pady=5)
    duration_entry.insert(0, class_edit['key'].split("_")[2])

    type_var = ctk.StringVar(value="Teoría" if class_edit['key'] in c_info else "Laboratorio")
    ctk.CTkOptionMenu(add_win,
                      values=["Teoría", "Laboratorio"],
                      variable=type_var, state="disabled").pack(pady=5)

    group_entry = ctk.CTkEntry(add_win, placeholder_text="Grupo(s)")
    group_entry.pack(pady=5)
    group_entry.insert(0, ", ".join(map(str, c_info[class_edit['key']]['grupo'])) if class_edit['key'] in c_info else ", ".join(map(str, l_info[class_edit['key']]['grupo'])))    

    # --- Save Handler ---
    def save_class():
        # print("Saving class...")
        global p_info, classes_edited_keys, labs_edited_keys
        name = name_entry.get()
        fac = fac_entry.get()
        dep = dep_entry.get()
        mat = mat_entry.get()
        professor = [int(p.strip()) for p in prof_entry.get().split(",")] if "," in prof_entry.get() else [int(prof_entry.get())]
        room = room_entry.get()
        day = day_var.get()
        start_hour = int(start_entry.get())
        duration = int(duration_entry.get())
        is_lab = (type_var.get() == "Laboratorio")
        group = [int(g.strip()) for g in group_entry.get().split(",")] if "," in group_entry.get() else [int(group_entry.get())]

        # Update data dictionary
        old_key = class_edit['key']
        print(f"Old key: {old_key}")
        new_key = f"{name}_{start_hour}_{duration}_{day}_{room}"
        info_dict = {
            "id": l_info[old_key]['id'] if old_key in l_info else c_info[old_key]['id'],
            "nombre": name,
            "facultad": fac,
            "dependencia": dep,
            "materia": mat,
            "codigo": f"{fac}{dep}{mat}",
            "profesor": professor,
            "grupo": group,
            "aula": room
        }

        cell_name = f"{c_info[old_key]['nombre']}\n{c_info[old_key]['grupo']}" if old_key in c_info else f"{l_info[old_key]['nombre']}\n{l_info[old_key]['grupo']}"

        for widget in window.winfo_children():
            if widget in lbs_ids:
                print(f'Widget text: {widget.cget("text")}')
                if isinstance(widget, Label) and widget.cget("text") == cell_name:
                    #Change label text
                    widget.config(text=f"{name}\n{group}")
                    break

        if is_lab:
            if old_key in l_info:
                del l_info[old_key]
        else:
            if old_key in c_info:
                del c_info[old_key]

        # Add the new entry
        if is_lab:
            l_info[new_key] = info_dict
            labs_edited_keys.append(new_key)
        else:
            c_info[new_key] = info_dict
            classes_edited_keys.append(new_key)
        
        class_edit['key'] = new_key

        # Close the edit window
        add_win.destroy()

    # --- Cancel Handler ---
    def cancel_edit():
        add_win.destroy()

    # --- Bind Save and Cancel ---
    ctk.CTkButton(add_win, text="Guardar", command=save_class).pack(pady=20)
    ctk.CTkButton(add_win, text="Cancelar", command=cancel_edit).pack(pady=5)

    add_win.transient(window)
    add_win.grab_set()
    window.wait_window(add_win)

edit_button = Button(window, text="Editar\nClase", command=open_edit_class_window, background="lightblue")
edit_button.place(x=int(screen_width*(14/15)), y=single_height*12)

def delete_selected_class():
    global class_edit, deleted_keys
    key = class_edit['key']
    group = c_info[key]['grupo'] if key in c_info else l_info[key]['grupo'] if key in l_info else None
    ids_to_delete = c_info[key]['id'] if key in c_info else l_info[key]['id'] if key in l_info else None
    cell_name = f"{c_info[key]['nombre']}\n{group}" if key in c_info else f"{l_info[key]['nombre']}\n{group}"
    print(cell_name)
    print("----------------------------------------")
    if key:
        # for widget in window.winfo_children():
        # if len(lbs_ids) == 0:
        #     break
        # if isinstance(widget, Label):
        #     if widget == lbs_ids[0]:
        #         lbs_ids.remove(widget) ##< Remove the label id from the list
        #         widget.destroy()
        # Remove from UI
        for widget in window.winfo_children():
            if widget in lbs_ids:
                print(f'Widget text: {widget.cget("text")}')
                if isinstance(widget, Label) and widget.cget("text") == cell_name:
                    widget.destroy()
                    break

        # Mark as deleted
        for id in ids_to_delete:
            deleted_keys.append(id)
        print(deleted_keys)

        # Remove from data dictionaries
        if key in c_info:
            del c_info[key]
        if key in l_info:
            del l_info[key]

        # Clear selection
        class_edit['key'] = None

delete_button = Button(window, text="Eliminar\nClase", command=delete_selected_class, background="red")
delete_button.place(x=int(screen_width*(14/15)), y=single_height*14)

window.mainloop() ##< Start the main loop of the window