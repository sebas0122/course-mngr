from tkinter import *
from tkinter import ttk, filedialog
from unicodedata import name

import customtkinter as ctk

from professor import Professor
from dnd import *
from courses_functions import connectSQL, retrieveDBTable, getClassesList, getProfessorsData, update_schedule_in_db, delete_class_in_db, addProfessorToDB

supabase_instance = connectSQL() ##< Connect to the database
courses_list = retrieveDBTable(supabase_instance, "materias") ##< Connect to the database and get the data as Course objects

ctk.set_appearance_mode("Light") ##< Set the appearance mode to light
ctk.set_default_color_theme("dark-blue")

window = Tk() ##< Create a window

window_bg_color = "#F0F1EF" ##< Set the background color of the window

window.attributes('-fullscreen', False)
window.configure(bg=window_bg_color) ##< Set the background color of the window
window.attributes('-zoomed', True)  ##< Maximize the window (windowed full-screen)
# window.state('zoomed') ##< Maximize the window (windowed full-screen)

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
single_height = int(screen_height / 22) ##< Set the height of a single cell

lab_displacement = int(2*single_width)-single_width ##< lab_displacement is to set the displacement of the labs cells in the grid (compared to the rooms). This is done to avoid overlapping with the rooms and avoid creating another xlimit list. The value is how many pixels is moved to the right.

# Add cells for hours
for hour in range(6, 22):
    label = Label(window,
                  image=pixel,
                  bg=window_bg_color,
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
                          compound="center",
                          bg=window_bg_color) ##< Create a label for the test
information_label.place(x=0, y=ylimit[-1]+2*single_height) ##< Set the rest of the labels at 7:00 and above

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
                        c_edited=labs_edited_keys) ##< Create the drag&drop label for the lab

            labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
        i+=1 ##< Increment the index for xlimit by 1

    return labels_ids ##< Return the list of labels ids

c, l, c_info, l_info = getClassesList(courses_list, 1) ##< Get the classes and labs for level 1
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

    courses_list = retrieveDBTable(supabase_instance, "materias") ##< Connect to the database and get the data as Course objects

    # Destroy all dnd_labels
    for widget in window.winfo_children():
        if len(lbs_ids) == 0:
            break
        if isinstance(widget, ctk.CTkLabel):
            if widget == lbs_ids[0]:
                lbs_ids.remove(widget) ##< Remove the label id from the list
                widget.destroy()

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

def open_add_class_window():
    add_win = Toplevel(window)
    add_win.title("Add Class")
    add_win.geometry(f"{int(screen_width*0.8)}x{int(screen_height*0.7)}")

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
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre")
    name_entry.pack(pady=5)

    # --- Row for code entries ---
    row_code_frame = ctk.CTkFrame(add_win, fg_color="transparent")
    row_code_frame.pack(pady=5)

    fac_column = ctk.CTkFrame(row_code_frame, fg_color="transparent")
    fac_column.pack(side=LEFT, padx=5)
    fac_entry = ctk.CTkEntry(fac_column, placeholder_text="Facultad", width=70)
    fac_entry.pack()
    fac_label = ctk.CTkLabel(fac_column, text="<Facultad>")
    fac_label.pack(pady=(2, 0))

    dep_column = ctk.CTkFrame(row_code_frame, fg_color="transparent")
    dep_column.pack(side=LEFT, padx=5)
    dep_entry = ctk.CTkEntry(dep_column, placeholder_text="Dependencia", width=90)
    dep_entry.pack()
    dep_label = ctk.CTkLabel(dep_column, text="<Dependencia>")
    dep_label.pack(pady=(2, 0))

    mat_entry = ctk.CTkEntry(row_code_frame, placeholder_text="Materia", width=60)
    mat_entry.pack(padx=5, side=LEFT)

    # small mapping for codes -> names (add more codes as needed)
    _fac_map = {"25": "Ingeniería"}
    _dep_map = {"98": "Electrónica"}    

    # Suggestion listboxes for course search
    name_suggestion_listbox = None
    code_suggestion_listbox = None

    def _update_code_labels(event=None):
        f = fac_entry.get().strip()
        d = dep_entry.get().strip()
        fac_label.configure(text=_fac_map.get(f, "<Facultad>"))
        dep_label.configure(text=_dep_map.get(d, "<Dependencia>"))

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
                code_suggestion_listbox = Listbox(row_code_frame, height=min(5, len(matches)), width=40)
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
            name_suggestion_listbox = Listbox(add_win, height=min(5, len(matches)), width=50)
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
    labs_container.pack(pady=5, fill='x')

    def add_lab_row(initial=None):
        """Add a single schedule row (type, room, day, start, duration) to labs_container."""
        row = ctk.CTkFrame(labs_container, fg_color="transparent")
        row.pack(pady=2)

        # type selector: Teoría or Laboratorio

        prof_column = ctk.CTkFrame(row, fg_color="transparent")
        prof_column.pack(side=LEFT, padx=5)
        prof_entry = ctk.CTkEntry(prof_column, placeholder_text="ID del Profesor")
        prof_entry.pack()
        prof_label = ctk.CTkLabel(prof_column, text="<Nombre del profesor>")
        prof_label.pack(pady=(2, 0))

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
                suggestion_listbox = Listbox(prof_column, height=min(5, len(matches)), width=30)
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
                prof_label.configure(text="<Nombre del profesor>")
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
            prof_label.configure(text=display_text)
        
        prof_entry.bind("<KeyRelease>", lambda e: (show_suggestions(e), _update_prof_label(e)))
        prof_entry.bind("<FocusOut>", lambda e: (_update_prof_label(e), hide_suggestions(e)))

        t_var = ctk.StringVar(value="Teoría")
        ctk.CTkOptionMenu(row, values=["Teoría", "Laboratorio"], variable=t_var, width=100).pack(side=LEFT, padx=2)

        r_entry = ctk.CTkEntry(row, placeholder_text="Aula", width=80)
        r_entry.pack(side=LEFT, padx=2)
        d_var = ctk.StringVar(value="Lunes")
        ctk.CTkOptionMenu(row, values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], variable=d_var, width=100).pack(side=LEFT, padx=2)
        s_entry = ctk.CTkEntry(row, placeholder_text="Inicio", width=70)
        s_entry.pack(side=LEFT, padx=2)
        dur_entry = ctk.CTkEntry(row, placeholder_text="Duración", width=70)
        dur_entry.pack(side=LEFT, padx=2)

        group_entry = ctk.CTkEntry(row, placeholder_text="Grupo(s)", width=50)
        group_entry.pack(side=LEFT, padx=2)

        remove_btn = ctk.CTkButton(row, text="-", width=30, command=lambda: remove_lab_row(row))
        remove_btn.pack(side=LEFT, padx=4)

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

    def remove_lab_row(frame):
        # remove the row from UI and internal list
        for r in labs_rows:
            if r['frame'] == frame:
                r['frame'].destroy()
                labs_rows.remove(r)
                break

    # add-row button (plus sign) - now adds any entry (theory or lab)
    add_lab_btn = ctk.CTkButton(add_win, text="+ Añadir Entrada", command=lambda: add_lab_row())
    add_lab_btn.pack(pady=2)

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
            key = f"{name}_{entry_start}_{entry_dur}_{entry_day}_{entry_room}"
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
                "aula": entry_room
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

        add_win.destroy()

    ctk.CTkButton(add_win, text="Guardar", command=save_class).pack(pady=20)

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

def update_database():
    update_schedule_in_db(supabase_instance, c_info, classes_edited_keys, False) ##< Function to update the database with the current schedule
    update_schedule_in_db(supabase_instance, l_info, labs_edited_keys, True) ##< Function to update the database with the current schedule
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
                if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == cell_name:
                    #Change label text
                    widget.configure(text=f"{name}\n{group}")
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
                if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == cell_name:
                    lbs_ids.remove(widget) ##< Remove the label id from the list
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

# Add this function before creating the export button
def export_to_excel():
    """Export the current database to an Excel file."""
    try:
        # Retrieve all data from the database
        dataframe = retrieveDBTable(supabase_instance, "materias")
        
        if dataframe is None or dataframe.empty:
            print("No data to export")
            return
        
        # Open file dialog to choose save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"materias_{opt.get().replace(' ', '_')}.xlsx"
        )
        
        if file_path:
            # Export to Excel
            dataframe.to_excel(file_path, index=False, sheet_name="Materias")
            print(f"Data exported successfully to {file_path}")
    except Exception as e:
        print(f"Error exporting to Excel: {e}")

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

def add_professor():
    add_win = Toplevel(window)
    add_win.title("Nuevo Profesor")
    add_win.geometry("700x500")

    # --- Form Fields ---
    name_entry = ctk.CTkEntry(add_win, placeholder_text="Nombre del Profesor")
    name_entry.pack(pady=20)

    id_entry = ctk.CTkEntry(add_win, placeholder_text="ID del Profesor")
    id_entry.pack(pady=5)

    email_entry = ctk.CTkEntry(add_win, placeholder_text="Email del Profesor", width=200)
    email_entry.pack(pady=5)

    cathedra_var = ctk.BooleanVar()
    cathedra_check = ctk.CTkCheckBox(add_win, text="¿Es cátedra?", variable=cathedra_var)
    cathedra_check.pack(pady=5)

    hiring_var = ctk.StringVar(value="NO ESPECIFICADO")
    ctk.CTkOptionMenu(add_win, values=["NO ESPECIFICADO","OCASIONAL","PLANTA","CÁTEDRA","CÁTEDRA CALENDARIO"],
                      variable=hiring_var, width=100).pack(pady=5)
    
    education_var = ctk.StringVar(value="NO ESPECIFICADO")
    ctk.CTkOptionMenu(add_win, values=["NO ESPECIFICADO", "PREGRADO", "MAESTRÍA", "DOCTORADO", "ESPECIALIZACIÓN"],
                      variable=education_var, width=100).pack(pady=5)


    # --- Save Handler ---
    def save_professor():

        prof = Professor(
            name = name_entry.get().strip(),
            id_number = int(id_entry.get().strip()),
            email = email_entry.get().strip(),
            cathedra = bool(cathedra_var.get()),
            hiring = hiring_var.get(),
            education = education_var.get()
        )

        if name:
            addProfessorToDB(supabase_instance, prof)
            add_win.destroy()

    ctk.CTkButton(add_win, text="Guardar", command=save_professor).pack(pady=20)

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