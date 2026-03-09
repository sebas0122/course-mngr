##
# @file main.py
# @brief Main application file for the Course Manager system
#
# This module implements the main GUI application for managing university course schedules.
# It provides a drag-and-drop interface for arranging classes and labs in a weekly schedule grid,
# with support for editing, adding, and deleting courses. The application connects to a Supabase
# database to store and retrieve course and professor information.
#
# @author Nelson Parra (nelson.parra@udea.edu.co)
# @date 2025

from tkinter import *
from tkinter import ttk, filedialog
from unicodedata import name

import customtkinter as ctk

from professor import Professor
from dnd import *
from courses_functions import connectSQL, retrieveDBTable, getClassesList, getProfessorsData, update_schedule_in_db, delete_class_in_db, addProfessorToDB, recalculate_hours_after_widget_removal

supabase_instance = connectSQL() ##< Connect to the database
courses_list = retrieveDBTable(supabase_instance, "materias") ##< Connect to the database and get the data as Course objects

ctk.set_appearance_mode("Light") ##< Set the appearance mode to light
ctk.set_default_color_theme("dark-blue")

window = Tk() ##< Create a window

window_bg_color = "#F0F1EF" ##< Set the background color of the window

window.attributes('-fullscreen', False)
window.configure(bg=window_bg_color) ##< Set the background color of the window
# window.attributes('-zoomed', True)  ##< Maximize the window (windowed full-screen)
window.state('zoomed') ##< Maximize the window (windowed full-screen)

# ensure window is mapped and layout updated, then use the window's actual size
window.update_idletasks()
screen_width = window.winfo_width() or window.winfo_screenwidth() ##< Get the usable window width (excludes taskbar when maximized)
screen_height = window.winfo_height() or window.winfo_screenheight() ##< Get the usable window height (excludes taskbar when maximized)

# fallback: on some systems winfo_width/height may be 1 — use update() if needed
if screen_width <= 1 or screen_height <= 1:
    window.update()
    screen_width = window.winfo_width() or window.winfo_screenwidth()
    screen_height = window.winfo_height() or window.winfo_screenheight()

pixel = PhotoImage(width=1, height=1)

single_width = int(screen_width / 14) ##< Set the width of a single cell

# Calculate single_height to fit schedule and leave space for information label
# Schedule needs: 2 header rows + 16 hour rows (6:00-21:00) = 18 rows
info_label_space = 80  # pixels reserved for information label at bottom
available_height = screen_height - info_label_space
single_height = int(available_height / 19)  ##< Automatically fits available space

#single_height = int((screen_height / 20)) ##< Set the height of a single cell
#label_height_multiplier = 1  ##< Multiplier for draggable label heights

lab_displacement = int(2*single_width)-single_width ##< lab_displacement is to set the displacement of the labs cells in the grid (compared to the rooms). This is done to avoid overlapping with the rooms and avoid creating another xlimit list. The value is how many pixels is moved to the right.

# Add cells for hours
for hour in range(6, 22):
    label = Label(window,
                  image=pixel,
                  bg=window_bg_color,
                  text=f"{hour}:00",
                  width=single_width-4,
                  height=int(single_height),
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
                          compound="center",
                          bg=window_bg_color) ##< Create a label for the test
#information_label.place(x=0, y=ylimit[-1]+2*single_height) ##< Set the rest of the labels at 7:00 and above
#information_label.place(x=0, y=min(ylimit[-1]+2*single_height, screen_height - 100))
information_label.place(x=0, y=ylimit[-1]+single_height)
# Add labels for days
for day in range(6):
    label = Label(window,
                  image=pixel,
                  text=days_es[day],
                  width=2*single_width-4,
                  height=single_height-4,
                  compound="center",
                  bg=window_bg_color) ##< Create a label for each day
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
                 bg=window_bg_color,
                 width=single_width-4,
                 height=single_height-4,
                 compound="center") ##< Create a label for the room
    room.place(x=xl, y=single_height) ##< Set the label position
    
    lab = Label(window,
                image=pixel,
                text="Lab",
                bg=window_bg_color,
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
horas_eliminadas_por_id = {}  # id (int) -> horas eliminadas (int)

##
# @brief Add classes and labs to the schedule grid
#
# This function creates draggable labels for all classes and labs and places them
# in the appropriate positions on the weekly schedule grid based on their day and time.
#
# @param classes List of class information for each day of the week
# @param labs List of lab information for each day of the week
# @param cl_information_label Dictionary mapping class keys to their detailed information
# @param lb_information_label Dictionary mapping lab keys to their detailed information
# @param professors_information Dictionary mapping professor IDs to their details
# @return List of widget IDs for the created class and lab labels
def add_classes_labs(classes, labs, cl_information_label, lb_information_label, professors_information):
    global colors_idx, class_colors_dict, screen_width, screen_height, single_width, single_height, lab_displacement, class_edit
    labels_ids = [] ##< Initialize the list of labels ids
    # Add classes (rooms) to schedule
    i = 0 ##< Initialize the index for xlimit
    print(f"Este es classes: {classes}")
    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

    # DEBUG: Print what we receive
    print("\n=== DEBUG add_classes_labs ===")
    for i, day in enumerate(classes):
        if day:
            print(f"  classes[{week_days[i]}]: {day}")
    for i, day in enumerate(labs):
        if day:
            print(f"  labs[{week_days[i]}]: {day}")
    print(f"  cl_information_label keys: {list(cl_information_label.keys())}")
    print(f"  lb_information_label keys: {list(lb_information_label.keys())}")
    print("=== END DEBUG ===\n")

    def make_widget_key(info, tipo_suffix):
        """Build widget_key consistently: codigo_sortedUniqueGroups_tipo"""
        codigo = info['codigo']
        grupos_str = "-".join(str(g) for g in sorted(set(info['grupo'])))
        return f"{codigo}_{grupos_str}_{tipo_suffix}"

    def build_widget_to_base_map(info_dict, tipo_suffix):
        wmap = {}
        for key_base, info in info_dict.items():
            widget_key = make_widget_key(info, tipo_suffix)
            day_idx = week_days.index(info['dia'])
            wmap[(widget_key, day_idx)] = key_base
        return wmap
    cl_widget_map = build_widget_to_base_map(cl_information_label, "0")
    lb_widget_map = build_widget_to_base_map(lb_information_label, "1")

    # DEBUG: Print the maps
    print("\n=== DEBUG widget maps ===")
    for k, v in cl_widget_map.items():
        print(f"  cl_map: {k} -> {v}")
    for k, v in lb_widget_map.items():
        print(f"  lb_map: {k} -> {v}")
    print("=== END DEBUG maps ===\n")

    for i, day in enumerate(classes): ##< Iterate over the classes
        for cl in day:
            key_base = cl_widget_map.get((cl, i))
            if not key_base:
                print(f"No se encontró key_base para widget_key: {cl} en día {i}")
                continue
            info = cl_information_label[key_base]
            if not info:
                print(f"No se encontró info para key: {cl}")
                continue
            #day_name = week_days[i]
            print("--------------------------------------------------------------------") 
            print("--------------------------------------------------------------------") 

            c_name = info['nombre']
            c_st_hour = int(info['hora_inicio'])
            c_duration = int(info['duracion'])
            c_room = info['aula']
            codigo = info['codigo']
            grupos = info['grupo']

            unique_grupos = sorted(set(grupos))
            cl_key = cl

            if c_name not in class_colors_dict:
                class_colors_dict[c_name] = colors[colors_idx]
                colors_idx += 1

            widget_text = f"{c_name}\n{unique_grupos}"

            dnd_label(window=window,
                        image=pixel,
                        geometry_width=screen_width,
                        geometry_height=screen_height,
                        lab_disp=0,
                        text=widget_text,
                        bg_color=class_colors_dict[c_name],
                        w=single_width,
                        h=(c_duration*single_height),
                        posx=xlimit[i],
                        posy=ylimit[c_st_hour-6],
                        hours=c_duration,
                        type="class",
                        room=c_room,
                        info_label=information_label,
                        cl_info=cl_information_label,
                        proffs_info=professors_information,
                        cell_to_edit=class_edit,
                        c_edited=classes_edited_keys,
                        initial_key=key_base) ##< Create the drag&drop label for the class

            labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
            labels_ids[-1].course_key = cl_key  # cl es el key único de la clase/lab, se asigna como atributo del widget para facilitar su identificación al editar/eliminar
        i+=1 ##< Increment the index for xlimit by 1

    # Add labs to schedule
    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    #i = 0 ##< Initialize the index for xlimit
    for i, day in enumerate(labs): ##< Iterate over the labs
        for cl in day:
            key_base = lb_widget_map.get((cl, i))
            if not key_base:
                print(f"No se encontró key_base para widget_key lab: {cl} en día {i}")
                continue
            info = lb_information_label[key_base]
            c_name = info['nombre']
            c_st_hour = int(info['hora_inicio'])
            c_duration = int(info['duracion'])
            c_room = info['aula']
            codigo = info['codigo']
            grupos = info['grupo']

            unique_grupos = sorted(set(grupos))
            cl_key = cl

            if c_name not in class_colors_dict:
                class_colors_dict[c_name] = colors[colors_idx]
                colors_idx += 1

            widget_text = f"{c_name}\n{unique_grupos}"

            dnd_label(window=window,
                        image=pixel,
                        geometry_width=screen_width,
                        geometry_height=screen_height,
                        lab_disp=lab_displacement,
                        text=widget_text,
                        bg_color=class_colors_dict[c_name],
                        w=single_width,
                        h=(c_duration*single_height),
                        posx=xlimit[i]+lab_displacement,
                        posy=ylimit[c_st_hour-6],
                        hours=c_duration,
                        type="lab",
                        room=c_room,
                        info_label=information_label,
                        cl_info=lb_information_label,
                        proffs_info=professors_information,
                        cell_to_edit=class_edit,
                        c_edited=labs_edited_keys,
                        initial_key=key_base) ##< Create the drag&drop label for the lab

            labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
            labels_ids[-1].course_key = cl_key  # cl es el key único de la clase/lab
        #i+=1 ##< Increment the index for xlimit by 1

    return labels_ids ##< Return the list of labels ids

c, l, c_info, l_info = getClassesList(courses_list, 1) ##< Get the classes and labs for level 1
p_info = getProfessorsData(supabase_instance)
lbs_ids = add_classes_labs(c, l, c_info, l_info, p_info) ##< Call the function to add classes and labs to the schedule

# Add dropdown menu for level selection

##
# @brief Change the displayed semester level
#
# This function is triggered when the user selects a different semester level from the
# dropdown menu. It clears the current schedule display and reloads it with the courses
# for the selected semester. The function refreshes the database connection to get the
# latest data before displaying.
#
# @note Modifies global variables: lbs_ids, c_info, l_info, colors_idx, class_colors_dict

def change_level():
    global lbs_ids, c_info, l_info, colors_idx, class_colors_dict, supabase_instance
    colors_idx = 0 ##< Reset the index for the colors
    class_colors_dict = {} ##< Reset the dictionary for the class colors

    courses_list = retrieveDBTable(supabase_instance, "materias") ##< Connect to the database and get the data as Course objects

    """# Destroy all dnd_labels
    for widget in window.winfo_children():
        if len(lbs_ids) == 0:
            break
        if isinstance(widget, ctk.CTkLabel):
            if widget == lbs_ids[0]:
                lbs_ids.remove(widget) ##< Remove the label id from the list
                widget.destroy()"""
    
    for widget in lbs_ids:
        widget.destroy()
    lbs_ids.clear()

    # IMPORTANT: Clear slot occupancy from the previous level
    clear_slot_occupancy()

    # Add classes and labs to the schedule based on the selected level
    if opt.get() == "Nivel 1":
        c, l, c_info, l_info = getClassesList(courses_list, 1) ##< Call the function to add classes and labs to the schedule
    elif opt.get() == "Nivel 2":
        c, l, c_info, l_info = getClassesList(courses_list, 2) ##< Call the function to add classes and labs to the schedule
    elif opt.get() == "Nivel 3":
        c, l, c_info, l_info = getClassesList(courses_list, 3)
    elif opt.get() == "Nivel 4":
        c, l, c_info, l_info = getClassesList(courses_list, 4)
    elif opt.get() == "Nivel 5":
        c, l, c_info, l_info = getClassesList(courses_list, 5)
    elif opt.get() == "Nivel 6":
        c, l, c_info, l_info = getClassesList(courses_list, 6)
    elif opt.get() == "Nivel 7":
        c, l, c_info, l_info = getClassesList(courses_list, 7)
    elif opt.get() == "Nivel 8":
        c, l, c_info, l_info = getClassesList(courses_list, 8)
    elif opt.get() == "Nivel 9":
        c, l, c_info, l_info = getClassesList(courses_list, 9)
    elif opt.get() == "Nivel 10":
        c, l, c_info, l_info = getClassesList(courses_list, 10)
    elif opt.get() == "E. Control":
        c, l, c_info, l_info = getClassesList(courses_list, 11)
    elif opt.get() == "E. Digitales":
        c, l, c_info, l_info = getClassesList(courses_list, 12)
    elif opt.get() == "E. Telecom":
        c, l, c_info, l_info = getClassesList(courses_list, 13)
    elif opt.get() == "E. Transversales":
        c, l, c_info, l_info = getClassesList(courses_list, 14)
    p_info = getProfessorsData(supabase_instance)
    lbs_ids = add_classes_labs(c, l, c_info, l_info, p_info)

# Dropdown options
level = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5", "Nivel 6", "Nivel 7", "Nivel 8", "Nivel 9", "E. Control", "E. Digitales", "E. Telecom", "E. Transversales"] 

# Selected option variable  
opt = StringVar(value="Nivel 1")

# Dropdown menu  
dd_menu = ctk.CTkOptionMenu(window,
                            variable=opt,
                            text_color="black",
                            values=level,
                            width=int(single_width*3/4),
                            fg_color="lightgray")
dd_menu.place(x=int(screen_width*(14/15)), y=single_height*2) ##< Set the position of the quit button

# Button to update label  
dd_button = ctk.CTkButton(window,
                          text="Aceptar",
                          text_color="black",
                          height=single_height,
                          width=int(single_width*3/4),
                          command=change_level,
                          fg_color="lightblue",
                          border_width=1,
                          border_color="black",
                          hover_color="#a3cde8") ##< Create a button to update the label
dd_button.place(x=int(screen_width*(14/15)), y=single_height*4) ##< Set the position of the quit button

##
# @brief Open dialog window for adding a new class or lab
#
# This function creates a popup window with a form for adding new courses to the schedule.
# It provides fields for entering course information including name, code, professors,
# schedule details, and room assignments. The window supports adding multiple schedule
# entries (theory and lab) for the same course.
#
# Features:
# - Auto-complete for course names and codes from existing database
# - Professor ID lookup with name display
# - Multiple schedule entry rows for theory and lab sessions
# - Form validation and data saving to schedule
#
# @note Updates global variables c_info, l_info, classes_edited_keys, labs_edited_keys
def open_add_class_window():
    add_win = Toplevel(window)
    add_win.title("Add Class")
    add_win.geometry(f"{int(screen_width*0.8)}x{int(screen_height*0.7)}")

    # Define larger fonts for the dialog
    DIALOG_FONT = ("Arial", 16)
    DIALOG_LABEL_FONT = ("Arial", 14)
    DIALOG_BUTTON_FONT = ("Arial", 15, "bold")
    DIALOG_ENTRY_WIDTH = 300
    DIALOG_ENTRY_HEIGHT = 38

    # Get all courses data for search
    all_courses_list = retrieveDBTable(supabase_instance, "materias")
    # Build a mapping of course code -> course name and vice versa
    _courses_map = {}  # code -> name
    _courses_reverse_map = {}  # name -> code
    _courses_details_map = {}  # code -> {facultad, dependencia, materia}
    
    for course in all_courses_list:
        code = course.get_codigo()
        name = course.nombre
        _courses_map[code] = name
        _courses_reverse_map[name.lower()] = code
        _courses_details_map[code] = {
            'facultad': str(course.facultad),
            'dependencia': str(course.dependencia),
            'materia': str(course.materia),
            'nombre': name
        }

    # --- Form Fields ---
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre", font=DIALOG_FONT, width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT)
    name_entry.pack(pady=10)

    # --- Row for code entries ---
    row_code_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_frame.pack(pady=10)

    fac_column = ctk.CTkFrame(row_code_frame, fg_color="transparent")
    fac_column.pack(side=LEFT, padx=10)
    fac_entry = ctk.CTkEntry(fac_column, placeholder_text="Facultad", width=120, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    fac_entry.pack()
    #fac_label = ctk.CTkLabel(fac_column, text="<Facultad>", font=DIALOG_LABEL_FONT)
    #fac_label.pack(pady=(4, 0))

    dep_column = ctk.CTkFrame(row_code_frame, fg_color="transparent")
    dep_column.pack(side=LEFT, padx=10)
    dep_entry = ctk.CTkEntry(dep_column, placeholder_text="Dependencia", width=150, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    dep_entry.pack()
    #dep_label = ctk.CTkLabel(dep_column, text="<Dependencia>", font=DIALOG_LABEL_FONT)
    #dep_label.pack(pady=(4, 0))

    mat_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Materia", width=120, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    mat_entry.pack(padx=10, side=LEFT)

    # small mapping for codes -> names (add more codes as needed)
    _fac_map = {"25": "Ingeniería"}
    _dep_map = {"98": "Electrónica"}    

    # Suggestion listboxes for course search
    name_suggestion_listbox = None
    code_suggestion_listbox = None

    def _update_code_labels(event=None):
        f = fac_entry.get().strip()
        d = dep_entry.get().strip()
        #fac_label.configure(text=_fac_map.get(f, "<Facultad>"))
        #dep_label.configure(text=_dep_map.get(d, "<Dependencia>"))

    def _autofill_from_code(event=None):
        """When code fields change, look up the course name and autofill."""
        nonlocal code_suggestion_listbox
        f = fac_entry.get().strip()
        d = dep_entry.get().strip()
        m = mat_entry.get().strip()
        
        # Close existing listbox if present
        if code_suggestion_listbox:
            code_suggestion_listbox.destroy()
            code_suggestion_listbox = None
        
        # Update labels
        _update_code_labels()
        
        # If we have a partial or complete code, show suggestions
        partial_code = f + d + m
        if partial_code:
            matches = []
            for code, details in _courses_details_map.items():
                if code.startswith(partial_code):
                    matches.append((code, details['nombre']))
            
            if matches:
                # Create suggestion listbox below the code entries
                code_suggestion_listbox = Listbox(row_code_frame, height=min(5, len(matches)), width=40, font=DIALOG_FONT)
                code_suggestion_listbox.pack(pady=(5, 0))
                
                for code, name in matches[:10]:  # Limit to 10 suggestions
                    code_suggestion_listbox.insert(END, f"{code} - {name}")
                
                def select_code_suggestion(event):
                    nonlocal code_suggestion_listbox
                    selection = code_suggestion_listbox.curselection()
                    if selection:
                        selected = code_suggestion_listbox.get(selection[0])
                        code = selected.split(" - ")[0]
                        details = _courses_details_map[code]
                        
                        # Autofill all fields
                        fac_entry.delete(0, END)
                        fac_entry.insert(0, details['facultad'])
                        dep_entry.delete(0, END)
                        dep_entry.insert(0, details['dependencia'])
                        mat_entry.delete(0, END)
                        mat_entry.insert(0, details['materia'])
                        name_entry.delete(0, END)
                        name_entry.insert(0, details['nombre'])
                        
                        _update_code_labels()
                    if code_suggestion_listbox:
                        code_suggestion_listbox.destroy()
                        code_suggestion_listbox = None
                
                code_suggestion_listbox.bind("<<ListboxSelect>>", select_code_suggestion)
                code_suggestion_listbox.bind("<Double-Button-1>", select_code_suggestion)

    def _autofill_from_name(event=None):
        """When name changes, look up the course code and autofill."""
        nonlocal name_suggestion_listbox
        search_text = name_entry.get().strip().lower()
        
        # Close existing listbox if present
        if name_suggestion_listbox:
            name_suggestion_listbox.destroy()
            name_suggestion_listbox = None
        
        if not search_text:
            return
        
        # Filter courses based on name search
        matches = []
        for name_lower, code in _courses_reverse_map.items():
            if search_text in name_lower:
                details = _courses_details_map[code]
                matches.append((code, details['nombre']))
        
        if matches:
            # Create suggestion listbox below name entry
            name_suggestion_listbox = Listbox(add_win, height=min(5, len(matches)), width=50, font=DIALOG_FONT)
            name_suggestion_listbox.pack(pady=(0, 5))
            
            for code, name in matches[:10]:  # Limit to 10 suggestions
                name_suggestion_listbox.insert(END, f"{code} - {name}")
            
            def select_name_suggestion(event):
                nonlocal name_suggestion_listbox
                selection = name_suggestion_listbox.curselection()
                if selection:
                    selected = name_suggestion_listbox.get(selection[0])
                    code = selected.split(" - ")[0]
                    details = _courses_details_map[code]
                    
                    # Autofill all fields
                    name_entry.delete(0, END)
                    name_entry.insert(0, details['nombre'])
                    fac_entry.delete(0, END)
                    fac_entry.insert(0, details['facultad'])
                    dep_entry.delete(0, END)
                    dep_entry.insert(0, details['dependencia'])
                    mat_entry.delete(0, END)
                    mat_entry.insert(0, details['materia'])
                    
                    _update_code_labels()
                if name_suggestion_listbox:
                    name_suggestion_listbox.destroy()
                    name_suggestion_listbox = None
            
            name_suggestion_listbox.bind("<<ListboxSelect>>", select_name_suggestion)
            name_suggestion_listbox.bind("<Double-Button-1>", select_name_suggestion)

    def _hide_name_suggestions(event=None):
        nonlocal name_suggestion_listbox
        window.after(200, lambda: name_suggestion_listbox.destroy() if name_suggestion_listbox else None)

    def _hide_code_suggestions(event=None):
        nonlocal code_suggestion_listbox
        window.after(200, lambda: code_suggestion_listbox.destroy() if code_suggestion_listbox else None)

    # bind updates so label changes while typing or after leaving the field
    name_entry.bind("<KeyRelease>", _autofill_from_name)
    name_entry.bind("<FocusOut>", _hide_name_suggestions)
    
    fac_entry.bind("<KeyRelease>", _autofill_from_code)
    fac_entry.bind("<FocusOut>", _hide_code_suggestions)
    dep_entry.bind("<KeyRelease>", _autofill_from_code)
    dep_entry.bind("<FocusOut>", _hide_code_suggestions)
    mat_entry.bind("<KeyRelease>", _autofill_from_code)
    mat_entry.bind("<FocusOut>", _hide_code_suggestions)

    # --- Labs multi-row UI ---
    labs_rows = []

    labs_container = ctk.CTkFrame(add_win, fg_color="transparent")
    labs_container.pack(pady=10, fill='x')

    MAX_ENTRIES = 8  # Maximum number of schedule entries allowed

    def add_lab_row(initial=None):
        """Add a single schedule row (type, room, day, start, duration) to labs_container."""
        if len(labs_rows) >= MAX_ENTRIES:
            return  # Do not add more than MAX_ENTRIES rows
        
        row = ctk.CTkFrame(labs_container, fg_color="transparent")
        row.pack(pady=6)

        # type selector: Teoría or Laboratorio

        prof_column = ctk.CTkFrame(row, fg_color="transparent")
        prof_column.pack(side=LEFT, padx=8)
        prof_entry = ctk.CTkEntry(prof_column, placeholder_text="ID/Nombre del Profesor", font=DIALOG_FONT, width=180, height=DIALOG_ENTRY_HEIGHT)
        prof_entry.pack()
        #prof_label = ctk.CTkLabel(prof_column, text="<Nombre del profesor>", font=DIALOG_LABEL_FONT)
        #prof_label.pack(pady=(4, 0))

        # Create suggestion listbox for professors
        p_info = getProfessorsData(supabase_instance)
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

        suggestion_listbox = None
    
        def show_suggestions(event=None):
            nonlocal suggestion_listbox
            full_text = prof_entry.get()
            
            # Get the current professor being typed (after last comma)
            if ',' in full_text:
                search_text = full_text.split(',')[-1].strip()
            else:
                search_text = full_text.strip()
            
            # Close existing listbox if present
            if suggestion_listbox:
                suggestion_listbox.destroy()
                suggestion_listbox = None
            
            if not search_text:
                return
            
            # Filter professors based on search
            matches = []
            for prof_id, prof_name in _p_map.items():
                if search_text.lower() in prof_id.lower() or search_text.lower() in prof_name.lower():
                    matches.append((prof_id, prof_name))
            
            if matches:
                # Create suggestion listbox
                suggestion_listbox = Listbox(prof_column, height=min(5, len(matches)), width=30, font=DIALOG_FONT)
                suggestion_listbox.pack()
                
                for prof_id, prof_name in matches[:10]:  # Limit to 10 suggestions
                    suggestion_listbox.insert(END, f"{prof_id} - {prof_name}")
                
                def select_suggestion(event):
                    nonlocal suggestion_listbox
                    selection = suggestion_listbox.curselection()
                    if selection:
                        selected = suggestion_listbox.get(selection[0])
                        prof_id = selected.split(" - ")[0]
                        
                        # Get existing professors (before last comma)
                        full_text = prof_entry.get()
                        if ',' in full_text:
                            existing_profs = ','.join(full_text.split(',')[:-1])
                            new_text = f"{existing_profs}, {prof_id}"
                        else:
                            new_text = prof_id
                        
                        prof_entry.delete(0, END)
                        prof_entry.insert(0, new_text)
                        _update_prof_label()
                    if suggestion_listbox:
                        suggestion_listbox.destroy()
                        suggestion_listbox = None
                
                suggestion_listbox.bind("<<ListboxSelect>>", select_suggestion)
                suggestion_listbox.bind("<Double-Button-1>", select_suggestion)
        
        def hide_suggestions(event=None):
            nonlocal suggestion_listbox
            # Small delay to allow click on listbox
            window.after(200, lambda: suggestion_listbox.destroy() if suggestion_listbox else None)
        
        def _update_prof_label(event=None):
            full_text = prof_entry.get().strip()
            
            if not full_text:
                #prof_label.configure(text="<Nombre del profesor>")
                return
            
            # Split by comma and get all professor IDs
            prof_ids = [p.strip() for p in full_text.split(',') if p.strip()]
            
            # Get names for all professors
            prof_names = []
            for prof_id in prof_ids:
                name = _p_map.get(prof_id, f"ID:{prof_id}")
                prof_names.append(name)
            
            # Join all names with comma
            display_text = ",\n".join(prof_names) if prof_names else "<Nombre del profesor>"
            #prof_names.configure(text=display_text)
        
        prof_entry.bind("<KeyRelease>", lambda e: (show_suggestions(e), _update_prof_label(e)))
        prof_entry.bind("<FocusOut>", lambda e: (_update_prof_label(e), hide_suggestions(e)))

        t_var = ctk.StringVar(value="Teoría")
        ctk.CTkOptionMenu(row, values=["Teoría", "Laboratorio"], variable=t_var, width=150, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT).pack(side=LEFT, padx=4)

        r_entry = ctk.CTkEntry(row, placeholder_text="Aula", width=120, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
        r_entry.pack(side=LEFT, padx=4)
        d_var = ctk.StringVar(value="Lunes")
        ctk.CTkOptionMenu(row, values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], variable=d_var, width=150, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT).pack(side=LEFT, padx=4)
        s_entry = ctk.CTkEntry(row, placeholder_text="Inicio", width=100, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
        s_entry.pack(side=LEFT, padx=4)
        dur_entry = ctk.CTkEntry(row, placeholder_text="Duración", width=110, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
        dur_entry.pack(side=LEFT, padx=4)

        group_entry = ctk.CTkEntry(row, placeholder_text="Grupo(s)", width=100, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
        group_entry.pack(side=LEFT, padx=4)

        remove_btn = ctk.CTkButton(row, text="-", width=40, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_BUTTON_FONT, command=lambda: remove_lab_row(row))
        remove_btn.pack(side=LEFT, padx=6)

        if initial:
            prof_entry.insert(0, initial.get('profesor', ''))
            t_var.set(initial.get('type', 'Teoría'))
            r_entry.insert(0, initial.get('aula', ''))
            d_var.set(initial.get('dia', 'Lunes'))
            s_entry.insert(0, str(initial.get('inicio', '')))
            dur_entry.insert(0, str(initial.get('duracion', '')))
            group_entry.insert(0, str(initial.get('grupo', '')))

        labs_rows.append({'frame': row, 'prof': prof_entry, 'type': t_var, 'room': r_entry, 'day_var': d_var, 'start': s_entry, 'duration': dur_entry, 'group': group_entry})
        # print(prof_entry, t_var, r_entry, d_var, s_entry, dur_entry, group_entry)

        # Disable the add button if we reached the limit
        if len(labs_rows) >= MAX_ENTRIES:
            add_lab_btn.configure(state="disabled")

    def remove_lab_row(frame):
        # remove the row from UI and internal list
        for r in labs_rows:
            if r['frame'] == frame:
                r['frame'].destroy()
                labs_rows.remove(r)
                break
        # Re-enable the add button if below the limit
        if len(labs_rows) < MAX_ENTRIES:
            add_lab_btn.configure(state="normal")    

    # add-row button (plus sign) - now adds any entry (theory or lab)
    add_lab_btn = ctk.CTkButton(add_win, text="+ Añadir Entrada", command=lambda: add_lab_row(), font=DIALOG_BUTTON_FONT, height=42, width=250)
    add_lab_btn.pack(pady=8)

    # start with no extra lab rows by default; user can add

    # --- Save Handler ---
    def save_class():
        print("Saving class...")
        """Save all rows: each row can be Teoría or Laboratorio. Name/code/prof/group come from the header fields."""
        global p_info, lbs_ids, classes_edited_keys, labs_edited_keys, colors_idx, class_colors_dict
        name = name_entry.get().strip()
        fac = fac_entry.get().strip()
        dep = dep_entry.get().strip()
        mat = mat_entry.get().strip()

        if len(labs_rows) == 0:
            print("No entries to add.")
            # nothing to add
            return

        # ensure color exists for the course name
        bg_color = class_colors_dict.get(name)
        if not bg_color:
            class_colors_dict[name] = colors[colors_idx]
            bg_color = class_colors_dict[name]
            colors_idx += 1

        for r in list(labs_rows):
            try:
                prof_text = r['prof'].get().strip()
                try:
                    professor_list = [int(p.strip()) for p in prof_text.split(",")] if "," in prof_text else [int(prof_text)]
                except Exception:
                    professor_list = [0]
                entry_room = r['room'].get().strip()
                entry_day = r['day_var'].get()
                entry_start = int(r['start'].get())
                entry_dur = int(r['duration'].get())
                entry_type = r['type'].get()
                group_text = r['group'].get().strip()
                try:
                    group_list = [int(g.strip()) for g in group_text.split(",")] if "," in group_text else [int(group_text)]
                except Exception:
                    group_list = [0]
            except Exception:
                # skip invalid row
                continue

            print(f"Adding entry: {name}, {fac}, {dep}, {mat}, Prof: {professor_list}, Room: {entry_room}, Day: {entry_day}, Start: {entry_start}, Dur: {entry_dur}, Type: {entry_type}, Group: {group_list}")

            is_lab = (entry_type == "Laboratorio")
            codigo = f"{fac}{dep}{mat}"
            grupos_str = "-".join(str(g) for g in sorted(set(group_list)))
            tipo = "1" if is_lab else "0"
            key = f"{codigo}_{grupos_str}_{tipo}"
            #key = f"{name}_{entry_start}_{entry_dur}_{entry_day}_{entry_room}"
            info_dict = {
                "id": [0],
                "nivel": int(opt.get().split(" ")[1]),
                "nombre": name,
                "facultad": fac,
                "dependencia": dep,
                "materia": mat,
                "codigo": f"{fac}{dep}{mat}",
                "profesor": professor_list,
                "grupo": group_list,
                "aula": entry_room,
                "hora_inicio": entry_start,
                "duracion": entry_dur,
                "dia": entry_day,
            }

            if is_lab:
                l_info[key] = info_dict
                labs_edited_keys.append(key)
            else:
                c_info[key] = info_dict
                classes_edited_keys.append(key)

            # Add UI label
            dnd_label(window=window,
                      image=pixel,
                      geometry_width=screen_width,
                      geometry_height=screen_height,
                      lab_disp=lab_displacement if is_lab else 0,
                      text=f"{name}\n{info_dict['grupo']}",
                      bg_color=bg_color,
                      w=single_width,
                      h=(entry_dur * single_height),
                      posx=xlimit[days_es.index(entry_day)] + (lab_displacement if is_lab else 0),
                      posy=ylimit[entry_start - 6],
                      hours=entry_dur,
                      type="lab" if is_lab else "class",
                      room=entry_room,
                      info_label=information_label,
                      cl_info=l_info if is_lab else c_info,
                      proffs_info=p_info,
                      cell_to_edit=class_edit,
                      c_edited=labs_edited_keys if is_lab else classes_edited_keys)

            lbs_ids.append(window.winfo_children()[-1])
            lbs_ids[-1].course_key = key

        add_win.destroy()

    ctk.CTkButton(add_win, text="Guardar", command=save_class, font=DIALOG_BUTTON_FONT, height=42, width=250).pack(pady=20)

# Button for adding a new class
add_button = ctk.CTkButton(window,
                           text="Añadir\nClase",
                           text_color="black",
                           height=int(single_height*3/2),
                           width=int(single_width*3/4),
                           command=open_add_class_window,
                           fg_color="lightyellow",
                           border_width=1,
                           border_color="black",
                           hover_color="#f7f1a8") ##< Create a button to add a new class
add_button.place(x=int(screen_width*(14/15)), y=single_height*8) ##< Set the position of the quit button

##
# @brief Save all schedule changes to the database
#
# This function commits all pending changes (edits, additions, deletions) to the
# Supabase database. It updates both theory classes and lab sessions, then clears
# the tracking lists and refreshes the display.
#
# @note Clears classes_edited_keys, labs_edited_keys, and deleted_keys after saving
def update_database():
    print("----------------------------------------------------------")
    print("----------------------------------------------------------")
    print("----------------------------------------------------------")
    print(f"clases editadas: {classes_edited_keys}")
    print(f"labs editados: {labs_edited_keys}")
    update_schedule_in_db(supabase_instance, c_info, classes_edited_keys, False) ##< Function to update the database with the current schedule
    update_schedule_in_db(supabase_instance, l_info, labs_edited_keys, True) ##< Function to update the database with the current schedule
    #recalculate_hours_after_widget_removal(supabase_instance, horas_eliminadas_por_id) ##< Function to recalculate the professors' load based on the updated schedule
    delete_class_in_db(supabase_instance, deleted_keys) ##< Function to delete the selected classes and labs from the database
    classes_edited_keys.clear() ##< Clear the list of classes edited keys
    labs_edited_keys.clear() ##< Clear the list of labs edited keys
    deleted_keys.clear() ##< Clear the list of deleted keys
    change_level() ##< Refresh the schedule display
# Button for updating database
update_button = ctk.CTkButton(window,
                              text="Guardar\nCambios",
                              text_color="black",
                              height=int(single_height*3/2),
                              width=int(single_width*3/4),
                              command=update_database,
                              fg_color="lightgreen",
                              border_width=1,
                              border_color="black",
                              hover_color="#a3cde8") ##< Create a button to update the database
update_button.place(x=int(screen_width*(14/15)), y=single_height*10)

##
# @brief Open dialog window for editing an existing class or lab
#
# This function creates a popup window with a form pre-filled with the currently
# selected course's information. Users can modify course details including professors,
# room assignments, duration, and groups. Some fields like code and start time are
# disabled to maintain schedule integrity.
#
# @note Requires class_edit['key'] to be set to a valid course key
# @note Updates c_info or l_info dictionaries with modified course information
def open_edit_class_window():
    def find_all_key_bases(widget_key, info_dict, tipo_suffix):
        """
        widget_key: group_type_code
        info_dict keys: day_classroom_type_hour_code (old format)
        """
        found = []
        parts = widget_key.rsplit("_", 1)
        if len(parts) != 2:
            return found
        tipo = parts[1]
        if tipo != tipo_suffix:
            return found
        for k, v in info_dict.items():
            codigo = v['codigo']
            grupos_str = "-".join(str(g) for g in sorted(set(v['grupo'])))
            expected = f"{codigo}_{grupos_str}_{tipo_suffix}"
            if expected == widget_key:
                found.append(k)
        return found

    widget_key = class_edit['key']
    if not widget_key:
        print("No hay clase seleccionada para editar.")
        return

    found_keys_class = find_all_key_bases(widget_key, c_info, "0")
    found_keys_lab = find_all_key_bases(widget_key, l_info, "1")

    is_lab = len(found_keys_lab) > 0 and len(found_keys_class) == 0

    if found_keys_class:
        edit_info = c_info[found_keys_class[0]]
    elif found_keys_lab:
        edit_info = l_info[found_keys_lab[0]]
    else:
        print(f"No se encontró info para key: {widget_key}")
        return

    add_win = Toplevel(window)
    add_win.title("Edit Class")
    add_win.geometry("600x800")
    DIALOG_FONT = ("Arial", 16)
    DIALOG_LABEL_FONT = ("Arial", 14)
    DIALOG_BUTTON_FONT = ("Arial", 15, "bold")
    DIALOG_ENTRY_WIDTH = 300
    DIALOG_ENTRY_HEIGHT = 38

    all_professors_list = retrieveDBTable(supabase_instance, "profesores")
    p_info = getProfessorsData(supabase_instance)

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

    # --- Form Fields using edit_info ---
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    name_entry.pack(pady=5)
    name_entry.insert(0, edit_info['nombre'])

    row_code_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_frame.pack(pady=5)

    fac_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Facultad", width=70, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    fac_entry.pack(padx=5, side=LEFT)
    fac_entry.insert(0, edit_info['facultad'])
    fac_entry.configure(state="disabled")

    dep_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Dependencia", width=90, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    dep_entry.pack(padx=5, side=LEFT)
    dep_entry.insert(0, edit_info['dependencia'])
    dep_entry.configure(state="disabled")   

    mat_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Materia", width=60, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    mat_entry.pack(padx=5, side=LEFT)
    mat_entry.insert(0, edit_info['materia'])
    mat_entry.configure(state="disabled")

    _fac_map = {"25": "Ingeniería"}
    _dep_map = {"98": "Electrónica"}

    row_code_labels_frame = ctk.CTkFrame(add_win, fg_color="transparent", height=30, width=400)
    row_code_labels_frame.pack(pady=2)

    fac_label = ctk.CTkLabel(row_code_labels_frame, text=_fac_map.get(str(edit_info['facultad']), "<Facultad>"), font=DIALOG_LABEL_FONT)
    fac_label.pack(padx=10, side=LEFT)

    dep_label = ctk.CTkLabel(row_code_labels_frame, text=_dep_map.get(str(edit_info['dependencia']), "<Dependencia>"), font=DIALOG_LABEL_FONT)
    dep_label.pack(padx=5, side=LEFT)

    row_prof_frame = ctk.CTkFrame(add_win, fg_color="transparent", height=80, width=400)
    row_prof_frame.pack(pady=5)

    prof_column = ctk.CTkFrame(row_prof_frame, fg_color="transparent", height=80, width=400)
    prof_column.pack(side=LEFT, padx=5)

    prof_entry = ctk.CTkEntry(prof_column, placeholder_text="ID del Profesor", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    prof_entry.pack()
    prof_entry.insert(0, ", ".join(map(str, edit_info['profesor'])))

    prof_label = ctk.CTkLabel(prof_column, text="<Nombre del profesor>", font=DIALOG_LABEL_FONT)
    prof_label.pack(pady=(2, 0))

    prof_suggestion_listbox = None

    def show_prof_suggestions(event=None):
        nonlocal prof_suggestion_listbox
        full_text = prof_entry.get()
        if ',' in full_text:
            search_text = full_text.split(',')[-1].strip()
        else:
            search_text = full_text.strip()
        if prof_suggestion_listbox:
            prof_suggestion_listbox.destroy()
            prof_suggestion_listbox = None
        if not search_text:
            return
        matches = [(pid, pname) for pid, pname in _p_map.items() if search_text.lower() in pid.lower() or search_text.lower() in pname.lower()]
        if matches:
            prof_suggestion_listbox = Listbox(prof_column, height=min(5, len(matches)), width=30, font=DIALOG_FONT)
            prof_suggestion_listbox.pack()
            for pid, pname in matches[:10]:
                prof_suggestion_listbox.insert(END, f"{pid} - {pname}")
            def select_prof_suggestion(event):
                nonlocal prof_suggestion_listbox
                selection = prof_suggestion_listbox.curselection()
                if selection:
                    selected = prof_suggestion_listbox.get(selection[0])
                    pid = selected.split(" - ")[0]
                    full_text = prof_entry.get()
                    if ',' in full_text:
                        existing = ','.join(full_text.split(',')[:-1])
                        new_text = f"{existing}, {pid}"
                    else:
                        new_text = pid
                    prof_entry.delete(0, END)
                    prof_entry.insert(0, new_text)
                    update_prof_label()
                if prof_suggestion_listbox:
                    prof_suggestion_listbox.destroy()
                    prof_suggestion_listbox = None
            prof_suggestion_listbox.bind("<<ListboxSelect>>", select_prof_suggestion)
            prof_suggestion_listbox.bind("<Double-Button-1>", select_prof_suggestion)

    def hide_prof_suggestions(event=None):
        nonlocal prof_suggestion_listbox
        add_win.after(200, lambda: prof_suggestion_listbox.destroy() if prof_suggestion_listbox else None)

    def update_prof_label(event=None):
        full_text = prof_entry.get().strip()
        if not full_text:
            prof_label.configure(text="<Nombre del profesor>")
            return
        prof_ids = [p.strip() for p in full_text.split(',') if p.strip()]
        prof_names = [_p_map.get(pid, f"ID:{pid}") for pid in prof_ids]
        prof_label.configure(text=",\n".join(prof_names) if prof_names else "<Nombre del profesor>")

    prof_entry.bind("<KeyRelease>", lambda e: (show_prof_suggestions(e), update_prof_label(e)))
    prof_entry.bind("<FocusOut>", lambda e: (update_prof_label(e), hide_prof_suggestions(e)))

    room_entry = ctk.CTkEntry(add_win, placeholder_text="Aula", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    room_entry.pack(pady=5)   
    room_entry.insert(0, edit_info['aula'])

    day_var = ctk.StringVar(value=edit_info['dia'])
    ctk.CTkOptionMenu(add_win, values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
                      variable=day_var, state="disabled", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT).pack(pady=5)

    start_entry = ctk.CTkEntry(add_win, placeholder_text="Hora de Inicio", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    start_entry.pack(pady=5)
    start_entry.insert(0, str(edit_info['hora_inicio']))
    start_entry.configure(state="disabled")

    duration_entry = ctk.CTkEntry(add_win, placeholder_text="Duración", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    duration_entry.pack(pady=5)
    duration_entry.insert(0, str(edit_info['duracion']))

    type_var = ctk.StringVar(value="Laboratorio" if is_lab else "Teoría")
    ctk.CTkOptionMenu(add_win, values=["Teoría", "Laboratorio"],
                      variable=type_var, state="disabled", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT).pack(pady=5)

    group_entry = ctk.CTkEntry(add_win, placeholder_text="Grupo(s)", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    group_entry.pack(pady=5)
    # Show unique sorted groups
    unique_edit_grupos = sorted(set(edit_info['grupo']))
    group_entry.insert(0, ", ".join(map(str, unique_edit_grupos)))

    def save_class():
        global p_info, classes_edited_keys, labs_edited_keys
        name = name_entry.get()
        fac = fac_entry.get()
        dep = dep_entry.get()
        mat = mat_entry.get()
        professor = [int(p.strip()) for p in prof_entry.get().split(",")] if "," in prof_entry.get() else [int(prof_entry.get())]
        room = room_entry.get()
        duration = int(duration_entry.get())
        is_lab_save = (type_var.get() == "Laboratorio")
        group = [int(g.strip()) for g in group_entry.get().split(",")] if "," in group_entry.get() else [int(group_entry.get())]

        codigo = f"{fac}{dep}{mat}"
        grupos_str = "-".join(str(g) for g in sorted(set(group)))
        tipo = "1" if is_lab_save else "0"
        new_widget_key = f"{codigo}_{grupos_str}_{tipo}"

        all_found = found_keys_lab if is_lab_save else found_keys_class
        target_dict = l_info if is_lab_save else c_info
        edited_list = labs_edited_keys if is_lab_save else classes_edited_keys

        keys_to_delete = []
        entries_to_add = []

        for fk in all_found:
            old_info = target_dict[fk]
            # Keep the old format for the c_info/l_info key
            # because on_release and update_schedule_in_db use it this way
            new_base_key = f"{codigo}_{old_info['hora_inicio']}_{duration}_{old_info['dia']}_{room}_{tipo}"
        
            info_dict = {
                    "id": old_info['id'],
                    "nombre": name,
                    "facultad": fac,
                    "dependencia": dep,
                    "materia": mat,
                    "codigo": codigo,
                    "codigos": old_info.get('codigos', [codigo]),
                    "profesor": professor,
                    "grupo": group,
                    "aula": room,
                    "hora_inicio": old_info['hora_inicio'],
                    "duracion": duration,
                    "dia": old_info['dia'],
                    "nivel": old_info.get('nivel', 1)
            }
            keys_to_delete.append(fk)
            entries_to_add.append((new_base_key, info_dict))
            edited_list.append(new_base_key)

        for fk in keys_to_delete:
            del target_dict[fk]
        for new_key, new_info in entries_to_add:
            target_dict[new_key] = new_info

        # Update widget in UI: search by course_key (old widget_key)
        for widget_w in window.winfo_children():
            if widget_w in lbs_ids:
                if isinstance(widget_w, ctk.CTkLabel) and hasattr(widget_w, "course_key") and widget_w.course_key == widget_key:
                    unique_g = sorted(set(group))
                    widget_w.configure(text=f"{name}\n{unique_g}")
                    widget_w.course_key = new_widget_key 
                    # Update the dnd_label key_info so that on_press continues to function
                    # Find the dnd_label that manages this widget  
                    for child in window.winfo_children():
                        if hasattr(child, 'key_info') and child is widget_w:
                            child.key_info = entries_to_add[0][0] if entries_to_add else child.key_info
        
        class_edit['key'] = new_widget_key
        add_win.destroy()

    def cancel_edit():
        add_win.destroy()

    ctk.CTkButton(add_win, text="Guardar", command=save_class, font=DIALOG_BUTTON_FONT, height=42, width=250).pack(pady=20)
    ctk.CTkButton(add_win, text="Cancelar", command=cancel_edit, font=DIALOG_BUTTON_FONT, height=42, width=250).pack(pady=5)

    add_win.transient(window)
    add_win.grab_set()
    window.wait_window(add_win)

edit_button = ctk.CTkButton(window,
                            text="Editar\nClase",
                            text_color="black",
                            height=int(single_height*3/2),
                            width=int(single_width*3/4),
                            command=open_edit_class_window,
                            fg_color="lightblue",
                            border_width=1,
                            border_color="black",
                            hover_color="#a3cde8") ##< Create a button to edit the selected class or lab
edit_button.place(x=int(screen_width*(14/15)), y=single_height*12)

##
# @brief Delete the currently selected class or lab from the schedule
#
# This function removes the selected course from both the GUI display and marks it
# for deletion from the database. The actual database deletion occurs when the user
# clicks the "Guardar Cambios" (Save Changes) button.
#
# @note Updates global variables: class_edit, deleted_keys, c_info, l_info, lbs_ids
def delete_selected_class():
    global class_edit, deleted_keys, horas_eliminadas_por_id
    print(f"class_edit before deletion: {class_edit}")
    key = class_edit['key']

    if not key:
        print("No hay clase seleccionada para eliminar.")
        return
    
    # Looking for the original key in the info dictionaries to get the ID for deletion
    def find_all_key_bases(widget_key, info_dict, tipo_suffix):
        """
        widget_key has the format: codigo_grupos_tipo (e.g., 2598521_8_1)
        info_dict keys have the old format: codigo_hora_dur_dia_aula_tipo
        We search for all entries in info_dict whose code+groups+type match.
        """
        found = []
        # Extract code and type from widget_key
        # format: {code}_{str_groups}_{type}
        # where str_groups can be "1", "1-2", "1-2-3", etc.
        parts = widget_key.rsplit("_", 1)  # split by the last "_" to get the type
        if len(parts) != 2:
            return found
        codigo_grupos = parts[0]  # ej: "2598521_8" o "2598521_1-2"
        tipo = parts[1]           # ej: "0" o "1"
        
        if tipo != tipo_suffix:
            return found

        for k, v in info_dict.items():
            codigo = v['codigo']
            grupos_str = "-".join(str(g) for g in sorted(set(v['grupo'])))
            expected_widget_key = f"{codigo}_{grupos_str}_{tipo_suffix}"
            if expected_widget_key == widget_key:
                found.append(k)
        return found
    
    found_keys_class = find_all_key_bases(key, c_info, "0")
    found_keys_lab = find_all_key_bases(key, l_info, "1")

    if not found_keys_class and not found_keys_lab:
        print(f"No se encontró info para key: {key}")
        return
    
    if found_keys_class:
        for class_key in found_keys_class:
            class_info_entry = c_info[class_key]
            class_codigos = class_info_entry.get('codigos', [class_info_entry['codigo']])
            class_grupos = set(class_info_entry['grupo'])
            class_nivel = class_info_entry.get('nivel')

            # Busca labs que compartan codigo, grupo y nivel con la clase
            labs_asociados = []
            for lab_key, lab_info_entry in list(l_info.items()):
                lab_codigos = lab_info_entry.get('codigos', [lab_info_entry['codigo']])
                lab_grupos = set(lab_info_entry['grupo'])
                lab_nivel = lab_info_entry.get('nivel')
                # Comparte algún codigo Y algún grupo Y mismo nivel
                if (set(class_codigos) & set(lab_codigos) and
                    class_grupos & lab_grupos and
                    class_nivel == lab_nivel):
                    labs_asociados.append(lab_key)

            for lab_key in labs_asociados:
                # Agregar IDs a deleted_keys
                for id in l_info[lab_key]['id']:
                    if id not in deleted_keys:
                        deleted_keys.append(id)
                # Marcar para que update_database lo procese
                if lab_key not in labs_edited_keys:
                    labs_edited_keys.append(lab_key)
                # Eliminar widget de la UI
                lab_widget_key = f"{l_info[lab_key]['codigo']}_{'- '.join(str(g) for g in sorted(set(l_info[lab_key]['grupo'])))}_1"
                # Buscar usando course_key del widget
                grupos_str = "-".join(str(g) for g in sorted(set(l_info[lab_key]['grupo'])))
                lab_widget_key = f"{l_info[lab_key]['codigo']}_{grupos_str}_1"
                for widget in list(window.winfo_children()):
                    if (widget in lbs_ids and
                        isinstance(widget, ctk.CTkLabel) and
                        hasattr(widget, "course_key") and
                        widget.course_key == lab_widget_key):
                        lbs_ids.remove(widget)
                        widget.destroy()
                # Eliminar del diccionario
                del l_info[lab_key]
                print(f"Lab asociado eliminado: {lab_key}")
    
    # Collect all IDs to delete and mark keys as edited for proper database update
    all_ids = []
    for fk in found_keys_class:
        all_ids.extend(c_info[fk]['id'])
        del c_info[fk]
    for fk in found_keys_lab:
        all_ids.extend(l_info[fk]['id'])
        del l_info[fk]

    # Remove from UI
    widgets_to_remove = []
    for widget in window.winfo_children():
        if widget in lbs_ids:
            print('----------------------------------------')
            print(f'Widget key: {widget.course_key}')
            print(f'key: {key}')
            print('----------------------------------------')
            if isinstance(widget, ctk.CTkLabel) and hasattr(widget, "course_key") and widget.course_key == key:
                widgets_to_remove.append(widget)

    for widget in widgets_to_remove:
        lbs_ids.remove(widget)
        widget.destroy()

    for id in all_ids:
        if id not in deleted_keys:
            deleted_keys.append(id)

    print(f"Intentando borrar key: {key}")
    print(f"Claves en c_info: {list(c_info.keys())}")
    print(f"Claves en l_info: {list(l_info.keys())}")
    print(f"Diccionarios horas por ID antes de eliminación: {deleted_keys}")

    # Clear selection
    class_edit['key'] = None  

delete_button = ctk.CTkButton(window,
                              text="Eliminar\nClase",
                              text_color="black",
                              height=int(single_height*3/2),
                              width=int(single_width*3/4),
                              command=delete_selected_class,
                              fg_color="red",
                              border_width=1,                              
                              border_color="black",
                              hover_color="#c50000") ##< Create a button to delete the selected class or lab
delete_button.place(x=int(screen_width*(14/15)), y=single_height*14)

##
# @brief Export all course data to an Excel file
#
# This function retrieves all courses and professors from the database and exports
# them to an Excel spreadsheet. The data is formatted according to the original
# import format with columns for course information, schedules, and professor details.
# The output is sorted by semester level and course code.
#
# Features:
# - Joins course data with professor information
# - Converts professor ID lists to pipe-separated strings
# - Handles multiple professors per course
# - Provides file dialog for choosing save location
#
# @note Requires pandas library for Excel export functionality
def export_to_excel():
    """Export the current database to an Excel file."""
    try:
        import pandas as pd
        
        # Retrieve all data from the database as Course objects
        courses_list = retrieveDBTable(supabase_instance, "materias")
        
        if not courses_list:
            print("No data to export")
            return
        
        # Retrieve all professors data
        professors_list = retrieveDBTable(supabase_instance, "profesores")
        
        # Create a mapping of identificacion -> Professor object for quick lookup
        professors_map = {prof.identificacion: prof for prof in professors_list}
        
        # Process each course and format data according to requirements
        excel_data = []
        # set for evit duplicates in case of multiple teoric courses with same professor
        teoricos_exportados = set()
        con = 0
        for course in courses_list:
            for idx, prof_id in enumerate(course.profesor):
                clave = (prof_id, course.facultad, course.dependencia, course.materia)
                if idx == 0:
                    if con < 5:
                        print(f"clave: {clave}")
                        print(f"teoricos_exportados: {teoricos_exportados}")
                        con += 1
                    if course.horas_teoricas != 0:
                        if clave in teoricos_exportados:
                            #print(clave)
                            horas = 0
                        else:
                            teoricos_exportados.add(clave)
                            horas = course.horas_teoricas
                            #print(f"Curso: {course.nombre}, teoria, Profesores: {course.profesor}, idx: {idx}, Horas asignadas: {horas}")
                    elif course.horas_practicas != 0:
                        horas = course.horas_practicas
                        # print(f"Curso: {course.nombre}, lab, Profesores: {course.profesor}, idx: {idx}, Horas asignadas: {horas}")
                    elif course.horas_tp != 0:
                        horas = course.horas_tp
                        # print(f"Curso: {course.nombre}, tp, Profesores: {course.profesor}, idx: {idx}, Horas asignadas: {horas}")
                    else:
                        horas = 0
                else:
                    horas = 0  # Los demás profesores no reciben horas en este registro

                prof = professors_map.get(prof_id)
                profesor_nombre = prof.nombre if prof else f"ID:{prof_id}"
                catedra_str = "SI" if prof and prof.catedra else "NO"
                cupo = getattr(course, 'cupo', 0)

                row = {
                    'Nivel': course.nivel,
                    'Facultad': course.facultad,
                    'Dependencia': course.dependencia,
                    'Materia': course.materia,
                    'Nombre': course.nombre,
                    'Grupo': course.grupo,
                    'Cupo': cupo,
                    'Aula': course.aula,
                    'Horario': course.horario,
                    'Cédula': prof_id,
                    'Profesor': profesor_nombre,
                    'Cátedra': catedra_str,
                    'Horas': horas
                }
                excel_data.append(row)
        
        # Create DataFrame with proper column order
        columns_order = ['Nivel', 'Facultad', 'Dependencia', 'Materia', 'Nombre', 
                        'Grupo', 'Cupo', 'Aula', 'Horario', 'Cédula', 
                        'Profesor', 'Cátedra', 'Horas']
        dataframe = pd.DataFrame(excel_data, columns=columns_order)
        
        # Add a temporary column for sorting by course code
        dataframe['_codigo_sort'] = dataframe['Facultad'].astype(str) + \
                                     dataframe['Dependencia'].astype(str) + \
                                     dataframe['Materia'].astype(str)
        
        # Sort: first by Nivel (ascending), then by course code to keep same courses together
        dataframe = dataframe.sort_values(by=['Nivel', '_codigo_sort', 'Grupo'], ascending=[True, True, True])

        # Remove the temporary sorting column
        dataframe = dataframe.drop(columns=['_codigo_sort'])
        
        # Reset index after sorting
        dataframe = dataframe.reset_index(drop=True)
        
        # Open file dialog to choose save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="Archivo_Materias_Exportado.xlsx"
        )
        
        if file_path:
            # Export to Excel
            dataframe.to_excel(file_path, index=False, sheet_name="Materias")
            print(f"Data exported successfully to {file_path}")
            print(f"Exported {len(excel_data)} courses")
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        import traceback
        traceback.print_exc()

# Add the Export button after the delete button
export_button = ctk.CTkButton(window,
                              text="Exportar\na Excel",
                              text_color="black",
                              height=int(single_height*3/2),
                              width=int(single_width*3/4),
                              command=export_to_excel,
                              fg_color="lightcyan",
                              border_width=1,
                              border_color="black",
                              hover_color="#a3e8e8")
export_button.place(x=int(screen_width*(14/15)), y=single_height*16)

##
# @brief Open dialog window for adding a new professor
#
# This function creates a popup window with a form for entering new professor
# information including name, ID number, email, cathedra status, hiring type,
# and education level. The data is validated and saved to the database.
#
# @note Creates a Professor SQLModel object and saves it using addProfessorToDB
def add_professor():
    add_win = Toplevel(window)
    add_win.title("Nuevo Profesor")
    add_win.geometry("700x600")

    # Define larger fonts for the dialog
    DIALOG_FONT = ("Arial", 18)
    DIALOG_BUTTON_FONT = ("Arial", 17, "bold")
    DIALOG_ENTRY_WIDTH = 320
    DIALOG_ENTRY_HEIGHT = 40

    # --- Form Fields ---
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre del Profesor", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    name_entry.pack(pady=20)

    id_entry = ctk.CTkEntry(add_win, placeholder_text="ID del Profesor", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    id_entry.pack(pady=5)

    email_entry = ctk.CTkEntry(add_win, placeholder_text="Email del Profesor", width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT)
    email_entry.pack(pady=5)

    cathedra_var = ctk.BooleanVar()
    cathedra_check = ctk.CTkCheckBox(add_win, text="¿Es cátedra?", variable=cathedra_var, font=DIALOG_FONT)
    cathedra_check.pack(pady=5)

    hiring_var = ctk.StringVar(value="NO ESPECIFICADO")
    ctk.CTkOptionMenu(add_win, values=["NO ESPECIFICADO","OCASIONAL","PLANTA","CÁTEDRA","CÁTEDRA CALENDARIO"],
                      variable=hiring_var, width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT).pack(pady=5)
    
    education_var = ctk.StringVar(value="NO ESPECIFICADO")
    ctk.CTkOptionMenu(add_win, values=["NO ESPECIFICADO", "PREGRADO", "MAESTRÍA", "DOCTORADO", "ESPECIALIZACIÓN"],
                      variable=education_var, width=DIALOG_ENTRY_WIDTH, height=DIALOG_ENTRY_HEIGHT, font=DIALOG_FONT).pack(pady=5)


    # --- Save Handler ---
    def save_professor():

        prof = Professor(
            nombre = name_entry.get().strip().upper(),
            identificacion = int(id_entry.get().strip()),
            correo = email_entry.get().strip(),
            catedra = bool(cathedra_var.get()),
            contratacion = hiring_var.get(),
            formacion = education_var.get()
        )

        if prof.nombre:
            addProfessorToDB(supabase_instance, prof)
            add_win.destroy()

    ctk.CTkButton(add_win, text="Guardar", command=save_professor, font=DIALOG_BUTTON_FONT, height=42, width=250).pack(pady=20)

# Button for adding a new professor
add_prof_button = ctk.CTkButton(window, 
                                text="Añadir\nProfesor",
                                text_color="black",
                                height=int(single_height*3/2),
                                width=int(single_width*3/4),
                                command=add_professor,
                                fg_color="lightpink",
                                border_width=1,
                                border_color="black",
                                hover_color="#f7a8d1") ##< Create a button to add a new professor
add_prof_button.place(x=int(screen_width*(14/15)), y=single_height*18) ##< Set the position of the quit button

window.mainloop() ##< Start the main loop of the window


def consultar_grupo(grupo_num):
    result = supabase_instance.table("materias").select("*").eq("grupo", grupo_num).execute()
    print(f"Cursos del grupo {grupo_num}:")
    for row in result.data:
        print(row)

if __name__ == "__main__":
    consultar_grupo(1)






