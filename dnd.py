##
# @file dnd.py
# @brief Drag-and-drop label functionality for course scheduling
#
# This module implements a custom drag-and-drop label widget for the course scheduler.
# It provides interactive labels that can be dragged around the schedule grid, with
# automatic snapping to valid time slots and responsive layout when multiple items
# occupy the same slot.
#
# @author Nelson Parra (nelson.parra@udea.edu.co)
# @date 2025

from tkinter import *
import customtkinter as ctk

xlimit = [] ##< xlimit is to locate x positions of the labels in the grid
ylimit = [] ##< ylimit is to locate y positions of the labels in the grid

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] ##< days is to set the names of the days of the week
days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"] ##< days_es is to set the names of the days of the week in Spanish

##< Occupancy map tracking which widgets are in each grid slot
# Key: (index_x, index_y, hours, type) -> list of Label widgets
slot_occupancy = {}  # key: (index_x, index_y, hours, type) -> list of Label widgets

##
# @brief Find all slots that overlap with a given time range
#
# @param index_x Day index
# @param start_y Starting hour index
# @param hours Duration in hours
# @param typ Type ("class" or "lab")
# @return List of overlapping slot keys
def find_overlapping_slots(index_x, start_y, hours, typ):
    """Find all existing slots that overlap with the given time range."""
    overlapping = []
    end_y = start_y + hours
    
    for slot_key in slot_occupancy.keys():
        slot_x, slot_start_y, slot_hours, slot_type = slot_key
        slot_end_y = slot_start_y + slot_hours
        
        # Check if same day and same type
        if slot_x == index_x and slot_type == typ:
            # Check if time ranges overlap
            if not (end_y <= slot_start_y or start_y >= slot_end_y):
                overlapping.append(slot_key)
    
    return overlapping


##
# @brief Clear all slot occupancy data
#
# Must be called when switching between levels/views to prevent
# widgets from different levels mixing in the layout calculations.
def clear_slot_occupancy():
    """Clear all slot occupancy data. Call this when switching levels/views."""
    global slot_occupancy
    slot_occupancy.clear()

##
# @brief Get all widgets that overlap with a time range
#
# @param index_x Day index
# @param start_y Starting hour index  
# @param hours Duration in hours
# @param typ Type ("class" or "lab")
# @return List of widgets that overlap
def get_overlapping_widgets(index_x, start_y, hours, typ):
    """Get all widgets that overlap with the given time range."""
    widgets = []
    overlapping_slots = find_overlapping_slots(index_x, start_y, hours, typ)
    
    for slot_key in overlapping_slots:
        for w in slot_occupancy.get(slot_key, []):
            if w.winfo_exists() and w not in widgets:
                widgets.append(w)
    
    return widgets

##
# @brief Get all widget info (widget, start_y, hours) for a day and type
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return List of tuples (widget, start_y, hours)
def get_all_widgets_info_for_day(index_x, typ):
    """Get all widgets with their time info for a specific day."""
    result = []
    for slot_key, widgets in slot_occupancy.items():
        slot_x, slot_start, slot_hours, slot_type = slot_key
        if slot_x == index_x and slot_type == typ:
            for w in widgets:
                if w.winfo_exists():
                    result.append((w, slot_start, slot_hours))
    return result

##
# @brief Calculate widgets overlapping at each specific hour
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Dictionary mapping hour -> list of widgets active at that hour
def get_widgets_per_hour(index_x, typ):
    """Get which widgets are active at each hour of the day."""
    hour_map = {}  # hour -> list of (widget, start_y, hours)
    
    all_widgets = get_all_widgets_info_for_day(index_x, typ)
    
    for widget, start_y, hours in all_widgets:
        for h in range(start_y, start_y + hours):
            if h not in hour_map:
                hour_map[h] = []
            hour_map[h].append((widget, start_y, hours))
    
    return hour_map

##
# @brief Assign consistent column positions to widgets
#
# Uses a greedy algorithm to assign column positions that remain
# consistent across all hours where a widget is active.
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Dictionary mapping widget -> column index
def assign_widget_columns(index_x, typ):
    """Assign column positions to widgets for consistent layout."""
    hour_map = get_widgets_per_hour(index_x, typ)
    
    if not hour_map:
        return {}
    
    # Get all unique widgets
    all_widgets = set()
    for widgets_at_hour in hour_map.values():
        for widget, _, _ in widgets_at_hour:
            all_widgets.add(widget)
    
    # Assign columns using greedy coloring
    widget_columns = {}
    
    # Sort hours to process in order
    sorted_hours = sorted(hour_map.keys())
    
    for hour in sorted_hours:
        widgets_at_hour = hour_map[hour]
        
        # Get widgets at this hour that don't have columns yet
        for widget, start_y, hours in widgets_at_hour:
            if widget not in widget_columns:
                # Find the first available column
                used_columns = set()
                for other_widget, _, _ in widgets_at_hour:
                    if other_widget in widget_columns:
                        used_columns.add(widget_columns[other_widget])
                
                # Assign first available column
                col = 0
                while col in used_columns:
                    col += 1
                widget_columns[widget] = col
    
    return widget_columns

##
# @brief Calculate the maximum columns needed for a day
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Maximum number of columns needed
def get_max_columns_for_day(index_x, typ):
    """Get the maximum number of overlapping widgets at any hour."""
    hour_map = get_widgets_per_hour(index_x, typ)
    
    if not hour_map:
        return 1
    
    return max(len(widgets) for widgets in hour_map.values())

##
# @brief Get the maximum overlaps for a specific widget's time range
#
# @param widget The widget to check
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Maximum number of overlapping widgets during this widget's hours
def get_max_overlaps_for_widget(widget, index_x, typ):
    """Get the maximum overlaps at any hour during this widget's time span."""
    # Find this widget's time range
    widget_start = None
    widget_hours = None
    
    for slot_key, widgets in slot_occupancy.items():
        if widget in widgets:
            slot_x, slot_start, slot_hours, slot_type = slot_key
            if slot_x == index_x and slot_type == typ:
                widget_start = slot_start
                widget_hours = slot_hours
                break
    
    if widget_start is None or widget_hours is None:
        return 1
    
    # Check max overlaps only during THIS widget's hours
    hour_map = get_widgets_per_hour(index_x, typ)
    max_overlaps = 1
    
    for hour in range(widget_start, widget_start + widget_hours):
        if hour in hour_map:
            count = len(hour_map[hour])
            max_overlaps = max(max_overlaps, count)
    
    return max_overlaps

##
# @brief Get widgets that overlap with a specific widget
#
# @param widget The widget to check
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Set of widgets that overlap with this widget
def get_widgets_overlapping_with(widget, index_x, typ):
    """Get all widgets that overlap with a specific widget's time range."""
    # Find this widget's time range
    widget_start = None
    widget_hours = None
    
    for slot_key, widgets in slot_occupancy.items():
        if widget in widgets:
            slot_x, slot_start, slot_hours, slot_type = slot_key
            if slot_x == index_x and slot_type == typ:
                widget_start = slot_start
                widget_hours = slot_hours
                break
    
    if widget_start is None or widget_hours is None:
        return set()
    
    # Find all widgets that overlap with this time range
    overlapping = set()
    hour_map = get_widgets_per_hour(index_x, typ)
    
    for hour in range(widget_start, widget_start + widget_hours):
        if hour in hour_map:
            for w, _, _ in hour_map[hour]:
                if w.winfo_exists():
                    overlapping.add(w)
    
    return overlapping

##
# @brief Assign columns only to widgets that actually overlap
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Dictionary mapping widget -> (column index, max columns in its group)
def assign_widget_columns_smart(index_x, typ):
    """Assign column positions considering only actual overlaps per widget."""
    all_widgets_info = get_all_widgets_info_for_day(index_x, typ)
    
    if not all_widgets_info:
        return {}
    
    # Sort by start time, then by duration (longer first for consistent ordering)
    all_widgets_info.sort(key=lambda x: (x[1], -x[2]))
    
    # Result: widget -> (column, max_columns_in_group)
    result = {}
    
    # Process each widget
    for widget, start_y, hours in all_widgets_info:
        if not widget.winfo_exists():
            continue
        
        # Get widgets that overlap with this one
        overlapping = get_widgets_overlapping_with(widget, index_x, typ)
        
        if len(overlapping) <= 1:
            # No overlaps - full width, column 0
            result[widget] = (0, 1)
        else:
            # Find used columns among overlapping widgets
            used_columns = {}
            for other in overlapping:
                if other in result and other is not widget:
                    col, _ = result[other]
                    used_columns[col] = other
            
            # Assign first available column
            col = 0
            while col in used_columns:
                col += 1
            
            # Max columns = number of overlapping widgets
            max_cols = len(overlapping)
            result[widget] = (col, max_cols)
            
            # Update max_cols for all overlapping widgets that were already assigned
            for other in overlapping:
                if other in result:
                    other_col, other_max = result[other]
                    result[other] = (other_col, max(other_max, max_cols))
    
    return result


 ##
# @brief Find all widgets in a connected overlap group
#
# Uses a union-find approach to group widgets that are transitively connected
# through overlaps. If A overlaps B and B overlaps C, then A, B, C are in the same group.
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return List of sets, each set contains widgets in the same overlap group
def find_overlap_groups(index_x, typ):
    """Find connected groups of overlapping widgets."""
    all_widgets_info = get_all_widgets_info_for_day(index_x, typ)
    
    if not all_widgets_info:
        return []
    
    # Deduplicate: a widget might appear in multiple slots if there's a bug
    seen_widgets = set()
    unique_widgets_info = []
    for widget, start_y, hours in all_widgets_info:
        if widget not in seen_widgets and widget.winfo_exists():
            seen_widgets.add(widget)
            unique_widgets_info.append((widget, start_y, hours))
    
    # Build adjacency: widget -> set of overlapping widgets
    adjacency = {}
    for widget, start_y, hours in all_widgets_info:
        if not widget.winfo_exists():
            continue
        overlapping = get_widgets_overlapping_with(widget, index_x, typ)
        adjacency[widget] = overlapping
    
    # Find connected components using DFS
    visited = set()
    groups = []
    
    def dfs(widget, group):
        if widget in visited:
            return
        visited.add(widget)
        group.add(widget)
        for neighbor in adjacency.get(widget, set()):
            if neighbor.winfo_exists():
                dfs(neighbor, group)
    
    for widget in adjacency.keys():
        if widget not in visited and widget.winfo_exists():
            group = set()
            dfs(widget, group)
            if group:
                groups.append(group)
    
    return groups

##
# @brief Assign columns to widgets within a connected group
#
# All widgets in the same group get columns based on the maximum overlap
# within that group, ensuring consistent widths.
#
# @param group Set of widgets in the same overlap group
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Dictionary mapping widget -> (column, max_columns)
def assign_columns_for_group(group, index_x, typ):
    """Assign column positions for widgets in a connected group."""
    if not group:
        return {}
    
    # Get widget info for sorting
    widget_info = {}
    for widget in group:
        for slot_key, widgets in slot_occupancy.items():
            if widget in widgets:
                slot_x, slot_start, slot_hours, slot_type = slot_key
                if slot_x == index_x and slot_type == typ:
                    widget_info[widget] = (slot_start, slot_hours)
                    break
    
    # Sort by start time, then by duration (longer first)
    sorted_widgets = sorted(
        [w for w in group if w in widget_info],
        key=lambda w: (widget_info[w][0], -widget_info[w][1])
    )
    
    if not sorted_widgets:
        return {}
    
    # Calculate maximum overlaps at any hour within this group
    hour_map = {}
    for widget in sorted_widgets:
        start_y, hours = widget_info[widget]
        for h in range(start_y, start_y + hours):
            if h not in hour_map:
                hour_map[h] = []
            hour_map[h].append(widget)
    
    max_overlaps = max(len(widgets) for widgets in hour_map.values()) if hour_map else 1

    # DEBUG
    print(f"\n=== assign_columns_for_group: day={index_x}, type={typ} ===")
    print(f"Group size: {len(group)}, Sorted widgets: {len(sorted_widgets)}")
    for w in sorted_widgets:
        start, hrs = widget_info[w]
        try:
            text = w.cget("text").split("\n")[1][:15]
        except:
            text = "?"
        print(f"  Widget '{text}' start={start}, hours={hrs}, hours_range={list(range(start, start+hrs))}")
    print(f"Hour map detail:")
    for h in sorted(hour_map.keys()):
        widget_texts = []
        for w in hour_map[h]:
            try:
                widget_texts.append(w.cget("text").split("\n")[1][:10])
            except:
                widget_texts.append("?")
        print(f"  Hour {h}: {widget_texts}")
    print(f"max_overlaps: {max_overlaps}")
    
    # Assign columns using greedy algorithm
    widget_columns = {}
    
    for widget in sorted_widgets:
        start_y, hours = widget_info[widget]
        widget_hours = set(range(start_y, start_y + hours))
        
        # Find columns used by overlapping widgets at any of this widget's hours
        used_columns = set()
        for h in range(start_y, start_y + hours):
            for other in hour_map.get(h, []):
                if other in widget_columns and other is not widget:
                    used_columns.add(widget_columns[other])    
        
        # DEBUG: Show which widgets contributed to used_columns
        contributing = {}
        for h in range(start_y, start_y + hours):
            for other in hour_map.get(h, []):
                if other in widget_columns and other is not widget:
                    try:
                        other_text = other.cget("text").split("\n")[1][:10]
                    except:
                        other_text = "?"
                    other_start, other_hours = widget_info[other]
                    contributing[other_text] = (widget_columns[other], other_start, other_hours, list(range(other_start, other_start + other_hours)))

        # Assign first available column
        col = 0
        while col in used_columns:
            col += 1
        
        widget_columns[widget] = col

        try:
            text = widget.cget("text").split("\n")[1][:15]
        except:
            text = "?"
        print(f"  Assigned col={col} to '{text}' (used_columns={used_columns})")

    # Option: Use group-wide max for all widgets to ensure no visual overlap
    global_max = max(len(widgets) for widgets in hour_map.values()) if hour_map else 1    

    # For each widget, compute its own max_cols based on the max direct overlaps
    # during its own time range. This allows widgets that don't overlap with the
    # full group to use wider columns.
    widget_max_cols = {}
    for widget in sorted_widgets:
        start_y, hours = widget_info[widget]
        local_max = 1
        for h in range(start_y, start_y + hours):
            count = len(hour_map.get(h, []))
            local_max = max(local_max, count)
        # Ensure the column index fits within local_max
        widget_max_cols[widget] = max(local_max, widget_columns[widget] + 1, global_max)
    
    print(f"Per-widget max_cols: {[(w.cget('text').split(chr(10))[1][:10] if w.winfo_exists() else '?', mc) for w, mc in widget_max_cols.items()]}")

    return {w: (col, widget_max_cols[w]) for w, col in widget_columns.items()}

##
# @brief Assign columns using connected group approach
#
# Groups widgets that are transitively connected through overlaps and assigns
# consistent column widths within each group.
#
# @param index_x Day index
# @param typ Type ("class" or "lab")
# @return Dictionary mapping widget -> (column index, max columns in group)
def assign_widget_columns_grouped(index_x, typ):
    """Assign column positions considering connected overlap groups."""
    groups = find_overlap_groups(index_x, typ)
    
    result = {}
    
    for group in groups:
        if len(group) == 1:
            # Single widget with no overlaps - full width
            widget = list(group)[0]
            if widget.winfo_exists():
                result[widget] = (0, 1)
        else:
            # Multiple widgets in group - assign columns based on group's max overlap
            group_columns = assign_columns_for_group(group, index_x, typ)
            result.update(group_columns)
    
    return result

    

##< Sample data for classes - format: "<class name>_<number of hours>"
# The blank elements create free space. First list is Monday, second is Tuesday, etc.
classes_list = [
    ["class2_2,1,2,3", "blank_2", "class3_3,3,4,5", "blank_5", "class4_4"],
    ["class2_2", "class2_2", "blank_4", "class_2"],
    ["class2_2", "blank_2", "class4_4", "class3_3", "blank_2", "class3_3"],
    ["class2_2", "class2_2", "blank_4", "class2_2"],
    ["class5_5", "blank_5", "class6_6"],
    ["class2_2", "blank_5", "class1_1"],
] ##< classes contains the classes for each day of the week, coded as <class name>_<number of hours>. The blank elements are used to create free space in the grid. First list is Monday, second is Tuesday, and so on. The number of hours must add maximum 16, which is the total number of hours in the schedule.

labs_list = [
    ["lab3_3", "blank_6", "lab3_3", "lab2_2"],
    ["blank_2", "lab3_3", "lab3_3", "lab3_3"],
    ["blank_4", "lab3_3", "lab3_3"],
    ["blank_2", "lab3_3", "lab3_3", "lab3_3"],
    ["lab3_3", "blank_6", "lab3_3", "lab2_2"],
    ["blank_4", "lab2_2", "lab1_1"],
] ##< labs contains the labs for each day of the week, coded as <lab name>_<number of hours>. The blank elements are used to create free space in the grid. First list is Monday, second is Tuesday, and so on. The number of hours must add maximum 16, which is the total number of hours in the schedule.

##
# @class dnd_label
# @brief Draggable label widget for course schedule grid
#
# This class creates interactive labels that can be dragged and dropped within a
# schedule grid. Labels automatically snap to valid grid positions and support
# responsive layout when multiple items occupy the same time slot. Each label
# represents a class or lab session and displays course information on click.
#
# Features:
# - Drag-and-drop functionality with grid snapping
# - Visual feedback during drag operations
# - Automatic layout adjustment for overlapping items
# - Information display panel integration
# - Edit tracking for database updates
class dnd_label:

    ##
    # @brief Constructor for draggable label
    #
    # Creates a customtkinter label with drag-and-drop functionality and registers it
    # in the slot occupancy map for responsive layout management.
    #
    # @param window Parent window/frame for the label
    # @param image PhotoImage object for label background
    # @param geometry_width Width of the parent window (for boundary checking)
    # @param geometry_height Height of the parent window (for boundary checking)
    # @param lab_disp Horizontal displacement for lab labels (0 for classes)
    # @param text Display text (course name and group)
    # @param bg_color Background color for the label
    # @param w Width of the label in pixels
    # @param h Height of the label in pixels (based on duration)
    # @param posx Initial X position in the grid
    # @param posy Initial Y position in the grid
    # @param hours Duration in hours (affects label height)
    # @param type Label type: "class" or "lab"
    # @param room Room/classroom assignment
    # @param info_label Reference to information display label
    # @param cl_info Dictionary with course information
    # @param proffs_info Dictionary with professor information
    # @param cell_to_edit Reference to currently selected cell for editing
    # @param c_edited List tracking edited course keys
    def __init__(self, window, image, geometry_width, geometry_height, lab_disp, text, bg_color, w, h, posx, posy, hours, type, room, info_label, cl_info, proffs_info, cell_to_edit, c_edited, initial_key=None):
        self.geometry_x = geometry_width ##< The width of the window
        self.geometry_y = geometry_height ##< The height of the window
        self.lab_displacement = lab_disp ##< The displacement of the lab label in the x axis
        self.w = w ##< The width of the label
        self.h = h ##< The height of the label
        self.image = image

        self.label = ctk.CTkLabel(window,
                            text=text,
                            fg_color=bg_color,
                            text_color="black",
                            width=self.w,
                            height=self.h,
                            corner_radius=6) ##< Create the label with the given parameters. The image is used to set the background of the label, the text is used to display the name of the class or lab, the bg_color is used to set the background color of the label, the width and height are used to set the size of the label, and the wraplength is used to set the maximum width of the text before it wraps to a new line.
        
        self.label.place(x=posx, y=posy)
        self.hours = hours ##< The number of hours the label will occupy in the grid
        self.type = type   ##< The type of the label (class or lab)
        self.room = room   ##< The room where the class/lab is held
        self.info_label = info_label ##< The label where the information of the course/lab will be displayed when the label is pressed
        self.cl_info = cl_info ##< The class information dictionary to be used in the info label
        self.proffs_info = proffs_info ##< The professors information dictionary to be used in the info label
        self.cell_to_edit = cell_to_edit ##< The cell to edit in the edit class window
        self.c_edited = c_edited ##< The edited classes keys
        self.label.bind("<Button-1>", self.on_press) ##< Bind the left mouse button to the on_press method
        self.label.bind("<B1-Motion>", self.on_drag) ##< Bind the left mouse button motion to the on_drag method
        self.label.bind("<ButtonRelease-1>", self.on_release) ##< Bind the left mouse button release to the on_release method

        # vínculo widget -> controlador
        self.label.dnd_ref = self

        # store initial pos and slot info
        self._initial_pos = (posx, posy)
        self._slot_key = None

        # Use initial_key directly if provided (most reliable method)
        if initial_key is not None and initial_key in cl_info:
            self.key_info = initial_key
        elif xlimit and ylimit:
            # Fallback: reconstruct key_info from position (for backwards compatibility)
            nombre = text.split("\n")[0]
            if type == "class":
                diff_x = [abs(x - posx) for x in xlimit]
                index_x = diff_x.index(min(diff_x))
                diff_y = [abs(y - posy) for y in ylimit]
                index_y = diff_y.index(min(diff_y))
                tipo = "0"
            else:
                diff_x = [abs(x - posx + lab_disp) for x in xlimit]
                index_x = diff_x.index(min(diff_x))
                diff_y = [abs(y - posy) for y in ylimit]
                index_y = diff_y.index(min(diff_y))
                tipo = "1"
            codigo = None
            for k, v in cl_info.items():
                if v['nombre'] == nombre and v.get('aula') == room:
                    codigo = v['codigo']
                    break
            if codigo:
                self.key_info = f'{codigo}_{int(index_y+6)}_{hours}_{days_es[index_x]}_{room}_{tipo}'
            else:
                self.key_info = next(
                    (k for k in cl_info if cl_info[k]['nombre'] == nombre and cl_info[k].get('aula') == room),
                    None
                )
        else:
            self.key_info = None

        self.label.info_key = self.key_info

        if xlimit and ylimit:
            try:
                self.register_to_slot(posx, posy)
            except Exception as e:
                print(f"Error in layout update: {e}")
    
    ##
    # @brief Compute grid slot position from pixel coordinates
    #
    # Converts pixel coordinates to grid slot indices by finding the closest
    # grid positions in the xlimit and ylimit arrays.
    #
    # @param posx X coordinate in pixels
    # @param posy Y coordinate in pixels
    # @return Tuple (index_x, index_y, hours, type) or None if limits not initialized
    def _compute_slot_from_pos(self, posx, posy):
        if not xlimit or not ylimit:
            return None
        # Normalize position by removing lab_displacement for labs
        normalized_x = posx - (self.lab_displacement if self.type == "lab" else 0)
        diff_x = [abs(x - normalized_x) for x in xlimit]
        index_x = diff_x.index(min(diff_x))
        diff_y = [abs(y - posy) for y in ylimit]
        index_y = diff_y.index(min(diff_y))
        return (index_x, index_y, self.hours, self.type)

    ##
    # @brief Register label in slot occupancy map and update layout
    #
    # Adds this label to the occupancy tracking for its current grid position
    # and triggers a layout update to handle multiple items in the same slot.
    #
    # @param posx X coordinate (uses current position if None)
    # @param posy Y coordinate (uses current position if None)
    def register_to_slot(self, posx=None, posy=None):
        # register label widget into slot_occupancy and trigger layout update
        if posx is None or posy is None:
            posx, posy = self.label.winfo_x(), self.label.winfo_y()
        slot = self._compute_slot_from_pos(posx, posy)
        if slot is None:
            return
        
        # DEBUG: Print slot registration
        try:
            text = self.label.cget("text").split("\n")[0][:15]
        except:
            text = "?"
        print(f"DEBUG register_to_slot: '{text}' -> slot={slot}")

        # FIRST: Remove this widget from ALL existing slots to prevent duplicates
        for existing_slot in list(slot_occupancy.keys()):
            lst = slot_occupancy[existing_slot]
            if self.label in lst:
                lst = [w for w in lst if w is not self.label]
                if lst:
                    slot_occupancy[existing_slot] = lst
                else:
                    del slot_occupancy[existing_slot]

        # ensure list exists and append if not present
        lst = slot_occupancy.setdefault(slot, [])
        # remove any stale or duplicate entries first
        lst = [w for w in lst if w.winfo_exists() and w is not self.label]
        # now add this label (ensuring no duplicates since we just removed it if present)
        lst.append(self.label)
        slot_occupancy[slot] = lst
        self._slot_key = slot
        #self._update_slot_layout(slot)
        # Force Tkinter to process all pending geometry (place/configure calls)
        # BEFORE calculating overlap layout, so winfo_x/winfo_y return correct values
        try:
            self.label.update_idletasks()
        except Exception:
            pass
        
        self._update_overlapping_layouts(slot)

    ##
    # @brief Remove label from slot occupancy map
    #
    # Removes this label from the occupancy tracking and triggers layout
    # update for remaining widgets in the slot.
    #
    # @param slot Slot tuple (index_x, index_y, hours, type)
    def unregister_from_slot(self, slot):
        if slot is None:
            return
        lst = slot_occupancy.get(slot, [])
        lst = [w for w in lst if w.winfo_exists() and w is not self.label]
        if lst:
            slot_occupancy[slot] = lst
            #self._update_slot_layout(slot)
        else:
            slot_occupancy.pop(slot, None)
        if self._slot_key == slot:
            self._slot_key = None
        # Update layout for remaining overlapping widgets
        if slot:
            index_x, index_y, hours, typ = slot
            self._update_all_overlapping_in_day(index_x, typ)
    

    ##
    # @brief Update layout for all overlapping widgets in a day
    #
    # @param index_x Day index
    # @param typ Type ("class" or "lab")
    def _update_all_overlapping_in_day(self, index_x, typ):
        """Recalculate layout for all widgets on a given using smart column assignment."""
        # First, clean up any stale entries in slot_occupancy for this day
        stale_keys = []
        for slot_key in list(slot_occupancy.keys()):
            slot_x, slot_start, slot_hours, slot_type = slot_key
            if slot_x == index_x and slot_type == typ:
                widgets = [w for w in slot_occupancy[slot_key] if w.winfo_exists()]
                if widgets:
                    slot_occupancy[slot_key] = widgets
                else:
                    stale_keys.append(slot_key)
        for key in stale_keys:
            del slot_occupancy[key]

        # Get column assignments for all widgets
        widget_columns = assign_widget_columns_grouped(index_x, typ)
        
        if not widget_columns:
            return            

        # Base x position
        base_x = xlimit[index_x] + (self.lab_displacement if typ == "lab" else 0)
        full_width = self.w

        print(f"\n--- _update_all_overlapping_in_day: day={index_x}, type={typ} ---")
        print(f"  base_x={base_x}, full_width={full_width}, lab_disp={self.lab_displacement if typ == 'lab' else 0}")
        print(f"  xlimit[{index_x}]={xlimit[index_x]}")

        """# Build hour_map for per-widget max_cols calculation
        hour_map = get_widgets_per_hour(index_x, typ)"""
        
        # Position each widget according to its column and overlap count
        for widget, (col, max_cols) in widget_columns.items():
            if not widget.winfo_exists():
                continue
            
            # Find this widget's start_y from slot_occupancy
            target_y = None
            for slot_key, widgets in slot_occupancy.items():
                if widget in widgets:
                    slot_x, slot_start, slot_hours, slot_type = slot_key
                    if slot_x == index_x and slot_type == typ:
                        target_y = ylimit[slot_start]
                        break
            
            if target_y is None:
                continue
            
            # For single widgets (no overlaps), restore full width and default font
            if max_cols == 1:
                per_w = full_width
                target_x = base_x
                new_wraplength = full_width - 5
                font_size = 14
            else:
                # Calculate width based on actual overlaps for THIS widget
                per_w = int(full_width / max(1, max_cols))
                target_x = base_x + col * per_w
                new_wraplength = max(per_w - 10, 20)
                font_size = max(8, min(14, int(per_w / 8)))

            try:
                text = widget.cget("text").split("\n")[1][:10]
            except:
                text = "?"
            print(f"  Widget '{text}': col={col}, max_cols={max_cols}, per_w={per_w}, target_x={target_x}, target_y={target_y}, current_x={widget.winfo_x()}, current_y={widget.winfo_y()}")
            
            # Obtener altura real del controlador
            dnd_controller = getattr(widget, 'dnd_ref', None)
            widget_height = dnd_controller.h if dnd_controller is not None else self.h

            try:
                # IMPORTANT: For CTkLabel, we must configure the widget's own width property
                # AND use place_configure to set the geometry. place_configure alone may not
                # resize a CTkLabel because customtkinter manages its own internal sizing.
                widget.configure(width=per_w, wraplength=new_wraplength, font=("Arial", font_size))
                widget.place_configure(x=target_x, y=target_y)
                # Force immediate visual update
                widget.update_idletasks()
            except Exception as e:
                print(f"Error in layout update: {e}")

    """##
    # @brief Update layout for all widgets in a slot
    #
    # Recalculates and applies positioning for all widgets sharing the same
    # grid slot. Widgets are arranged side-by-side with equal width distribution.
    #
    # @param slot Slot tuple (index_x, index_y, hours, type)
    def _update_slot_layout(self, slot):
        if slot not in slot_occupancy:
            return
        widgets = [w for w in slot_occupancy[slot] if w.winfo_exists()]
        if not widgets:
            slot_occupancy.pop(slot, None)
            return
        slot_occupancy[slot] = widgets

        index_x, index_y, hours, typ = slot
        cell_width = self.w
        n = max(1, len(widgets))
        per_w = int(cell_width / n)
        
        # Base x already at grid position; add lab_displacement once for all labs
        base_x = xlimit[index_x] + (self.lab_displacement if typ == "lab" else 0)
        
        for idx, w in enumerate(widgets):
            target_y = ylimit[index_y]
            target_x = base_x + idx * per_w  # No conditional displacement here
            try:
                w.place_configure(x=target_x, y=target_y, width=per_w)
            except Exception as e:
                print(f"Error in layout update: {e}")
                pass"""

    ##
    # @brief Update layouts for all slots that overlap with the given slot
    #
    # @param slot The slot that was just registered/changed
    def _update_overlapping_layouts(self, slot):
        if slot is None:
            return
        index_x, index_y, hours, typ = slot
        
        # Update the entire day's layout for proper column assignment
        self._update_all_overlapping_in_day(index_x, typ)      
    
    ##
    # @brief Update layout for a slot considering all overlapping widgets
    #
    # @param slot Slot tuple (index_x, index_y, hours, type)
    def _update_slot_layout_with_overlaps(self, slot):
        if slot not in slot_occupancy:
            return
            
        index_x, index_y, hours, typ = slot

        # Use the day-wide layout update for consistency
        self._update_all_overlapping_in_day(index_x, typ)
        
        # Get ALL widgets that overlap with this time range
        all_overlapping = get_overlapping_widgets(index_x, index_y, hours, typ)
        
        if not all_overlapping:
            return
        
        # Calculate width division based on maximum overlaps at any hour
        max_overlaps = self._calculate_max_overlaps_at_hour(index_x, index_y, hours, typ)
        
        cell_width = self.w
        per_w = int(cell_width / max(1, max_overlaps))
        
        # Get widgets in THIS specific slot
        widgets = [w for w in slot_occupancy[slot] if w.winfo_exists()]
        if not widgets:
            slot_occupancy.pop(slot, None)
            return
        slot_occupancy[slot] = widgets
        
        # Assign positions based on overlap order
        base_x = xlimit[index_x] + (self.lab_displacement if typ == "lab" else 0)
        
        # Determine position index for each widget in this slot
        for w in widgets:
            # Find this widget's index among all overlapping widgets
            position_idx = self._get_widget_position_index(w, index_x, index_y, hours, typ)
            target_x = base_x + position_idx * per_w
            target_y = ylimit[index_y]
            
            try:
                w.place_configure(x=target_x, y=target_y, width=per_w)
            except Exception as e:
                print(f"Error in layout update: {e}")

    ##
    # @brief Calculate maximum number of overlapping widgets at any hour
    #
    # @param index_x Day index
    # @param start_y Starting hour index
    # @param hours Duration
    # @param typ Type
    # @return Maximum overlap count
    def _calculate_max_overlaps_at_hour(self, index_x, start_y, hours, typ):
        """Calculate the maximum number of widgets overlapping at any single hour."""
        end_y = start_y + hours
        max_count = 1
        
        # Check each hour in the range
        for hour in range(start_y, end_y):
            count = 0
            for slot_key, widgets in slot_occupancy.items():
                slot_x, slot_start, slot_hours, slot_type = slot_key
                slot_end = slot_start + slot_hours
                
                if slot_x == index_x and slot_type == typ:
                    # Check if this hour falls within the slot's range
                    if slot_start <= hour < slot_end:
                        count += len([w for w in widgets if w.winfo_exists()])
            
            max_count = max(max_count, count)
        
        return max_count

    ##
    # @brief Get position index for a widget among overlapping widgets
    #
    # @param widget The widget to find position for
    # @param index_x Day index
    # @param start_y Starting hour
    # @param hours Duration
    # @param typ Type
    # @return Position index (0, 1, 2, ...)
    def _get_widget_position_index(self, widget, index_x, start_y, hours, typ):
        """Determine the horizontal position index for a widget among overlapping ones."""
        all_overlapping = get_overlapping_widgets(index_x, start_y, hours, typ)
        
        # Sort widgets by their slot's start time for consistent ordering
        def get_start_time(w):
            for slot_key, widgets in slot_occupancy.items():
                if w in widgets:
                    return slot_key[1]  # Return start_y
            return 0
        
        all_overlapping.sort(key=get_start_time)
        
        try:
            return all_overlapping.index(widget)
        except ValueError:
            return 0
        
    ##
    # @brief Update layout for all widgets in a slot (legacy method)
    #
    # Recalculates and applies positioning for all widgets sharing the same
    # grid slot. Widgets are arranged side-by-side with equal width distribution.
    #
    # @param slot Slot tuple (index_x, index_y, hours, type)
    def _update_slot_layout(self, slot):
        # Use the new overlap-aware method
        self._update_slot_layout_with_overlaps(slot)    

    ##
    # @brief Mouse press event handler
    #
    # Captures the initial mouse position when the label is clicked and updates
    # the information panel with course details. Also handles visual feedback
    # by darkening the label during drag operations.
    #
    # @param event Tkinter event object containing mouse coordinates
    def on_press(self, event):
        self.x = event.x
        self.y = event.y

        # Store the initial position to detect if a real drag occurred
        self._drag_start_x = self.label.winfo_x()
        self._drag_start_y = self.label.winfo_y()
        self._did_drag = False

        # Lift this widget above all others during drag to prevent z-order flickering
        self.label.lift()

        # Store original dimensions to restore during drag (prevents deformation)
        self._drag_width = self.label.winfo_width()
        self._drag_height = self.label.winfo_height()

        # Restore previously active label's appearance
        prev = getattr(dnd_label, "active_label", None)
        if prev is not None and prev is not self:
            try:
                prev.label.configure(fg_color=getattr(prev, "_prev_fg", prev.label.cget("fg_color")), text_color="black")
            except Exception:
                pass

        if getattr(dnd_label, "active_label", None) is not self:
            self._prev_fg = self.label.cget("fg_color")
            self.label.configure(fg_color="#444444", text_color="white")
            dnd_label.active_label = self

        key_info = self.key_info    

        nombre_completo = self.label.cget("text")
        nombre = nombre_completo.split("\n")[0]

        # Fallback: if key_info was never set or doesn't exist in cl_info
        if key_info is None or key_info not in self.cl_info:
            key_info = next(
                (
                    k for k, v in self.cl_info.items()
                    if v['nombre'] == nombre and v.get('aula') == self.room
                ),
                None
            )
            if key_info:
                self.key_info = key_info

        # Final check: if key still not found, show error and return
        if key_info is None or key_info not in self.cl_info:
            print(f"ERROR: Key not found in cl_info: {key_info}")
            print(f"Available keys: {[k for k in self.cl_info if nombre in k]}")
            return

        self.cell_to_edit['key'] = getattr(self.label, 'course_key', None)

        # Build info text in a clean, maintainable way
        info = self.cl_info[key_info]
        professors = []
        for pid in info['profesor']:
            prof_data = self.proffs_info.get(f'{pid}')
            if prof_data and isinstance(prof_data, dict) and 'name' in prof_data:
                professors.append(prof_data['name'])
            else:
                professors.append(f"ID:{pid}")
        tipo_materia = 'Teoría' if self.type == 'class' else 'Laboratorio'

        info_text = (
            f"Código de materia: {info['codigo']}"
            f"    |    Profesores: {', '.join(professors)}\n\n"
            f"Grupos: {', '.join(map(str, info['grupo']))}"
            f"    |    ID Profesores: {', '.join(map(str, info['profesor']))}\n\n"
            f"Tipo de materia: {tipo_materia}"
            f"    |    Aula: {info['aula']}"
        )

        self.info_label.configure(text=info_text)
        ## Shows in GUI the information of the course/lab being moved
        """if(len(self.cl_info[key_info]['grupo'])>5):
            self.info_label.configure(text=f"Código de materia: {self.cl_info[key_info]['codigo']}\t\t\t\tProfesores: {', '.join(professors)}\n\nGrupos: {', '.join(map(str, self.cl_info[key_info]['grupo']))}\t\t\t\tID Profesores: {', '.join(map(str, self.cl_info[key_info]['profesor']))}\n\nTipo de materia: {'Teoría' if self.type == 'class' else 'Laboratorio'}\t\t\t\tAula: {self.cl_info[key_info]['aula']}") ##< Set the text of the info label to the course code, groups, and professors of the label being moved
        else:
            self.info_label.configure(text=f"Código de materia: {self.cl_info[key_info]['codigo']}\t\tProfesores: {', '.join(professors)}\n\nGrupos: {', '.join(map(str, self.cl_info[key_info]['grupo']))}\t\t\t\tID Profesores: {', '.join(map(str, self.cl_info[key_info]['profesor']))}\n\nTipo de materia: {'Teoría' if self.type == 'class' else 'Laboratorio'}\t\tAula: {self.cl_info[key_info]['aula']}") ##< Set the text of the info label to the course code, groups, and professors of the label being moved
"""
    ##
    # @brief Mouse drag event handler
    #
    # Updates the label position to follow the mouse during drag operations.
    # The label moves continuously as the mouse is dragged.
    #
    # @param event Tkinter event object containing mouse coordinates
    def on_drag(self, event):
        x = self.label.winfo_x() - self.x + event.x ##< Get the new x position of the label
        y = self.label.winfo_y() - self.y + event.y ##< Get the new y position of the label
        # Use place_configure with fixed width/height to prevent deformation during drag
        self.label.place_configure(x=x, y=y)
        self._did_drag = True  # Mark that an actual drag occurred

    ##
    # @brief Mouse release event handler
    #
    # Handles the end of a drag operation by snapping the label to the nearest
    # valid grid position and updating the course information dictionaries. Also
    # manages slot occupancy for responsive layout and prevents labels from being
    # dragged outside the window boundaries.
    #
    # @param event Tkinter event object containing final mouse coordinates
    def on_release(self, event):
        # If no actual drag occurred (just a click), skip all repositioning logic
        if not getattr(self, '_did_drag', False):
            return

        print("on_release: x=%d, y=%d" % (self.label.winfo_x(), self.label.winfo_y())) ##< Print the position of the label when it is released

        if self.label.winfo_x() < 0 and self.label.winfo_y() < 0: ##< Check if the label is moved out of the window by the top left corner
            self.label.place(x=0, y=0) ##< Move the label back to the original position
        elif self.label.winfo_x() < 0: ##< Check if the label is moved out of the window only in the x axis to the left
            self.label.place(x=0, y=self.label.winfo_y()) ##< Move the label back to the original position in the x axis
        elif self.label.winfo_y() < 0: ##< Check if the label is moved out of the window only in the y axis to the top
            self.label.place(x=self.label.winfo_x(), y=0) ##< Move the label back to the original position in the y axis

        if self.label.winfo_x() + self.label.winfo_width() > self.geometry_x and self.label.winfo_y() + self.label.winfo_height() > self.geometry_y: ##< Check if the label is moved out of the window by the bottom right corner
            self.label.place(x=self.geometry_x - self.label.winfo_width(), y=self.geometry_y - self.label.winfo_height()) ##< Move the label back to the original position in both axes
        elif self.label.winfo_x() + self.label.winfo_width() > self.geometry_x: ##< Check if the label is moved out of the window only in the x axis to the right
            self.label.place(x=self.geometry_x - self.label.winfo_width(), y=self.label.winfo_y()) ##< Move the label back to the original position in the x axis
        elif self.label.winfo_y() + self.label.winfo_height() > self.geometry_y:
            self.label.place(x=self.label.winfo_x(), y=self.geometry_y - self.label.winfo_height())

        # Check if a label it is moved out of the grid
        if self.type == "class": ##< Check if the label is a class
            diff_x = [abs(x - self.label.winfo_x()) for x in xlimit] ##< Get the difference between the x position of the label and the x positions of the grid
            index_x = diff_x.index(min(diff_x)) ##< Get the index of the minimum difference in the x axis. This gives the closest x (day) position in the grid to the label.
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit] ##< Get the difference between the y position of the label and the y positions of the grid
            index_y = diff_y.index(min(diff_y)) ##< Get the index of the minimum difference in the y axis. This gives the closest y (hour) position in the grid to the label.
            # print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00') ##< Print the position of the label when it is released

            # CLAMP index_y: Ensure label doesn't extend past grid bottom
            # If schedule has 16 hours (6:00-22:00), ylimit has 16 entries (indices 0-15)
            # A 3-hour class can start at index 13 max (hour 19), ending at hour 22
            max_valid_index_y = len(ylimit) - self.hours
            if index_y > max_valid_index_y:
                index_y = max(0, max_valid_index_y)

            # Calculate the FINAL snapped position BEFORE any registration
            final_x = xlimit[index_x]
            final_y = ylimit[index_y]

            self.label.place(x=final_x, y=final_y)

            # Force Tkinter to update the widget's position immediately
            self.label.update_idletasks()

            old_key = self.key_info
            nombre = self.label.cget("text").split("\n")[0]
            new_day = days_es[index_x]
            new_hour = int(index_y + 6)

            old_info = self.cl_info.get(old_key)
            if old_info:
                codigo = old_info['codigo']
            else:
                codigo = None
                for k, v in self.cl_info.items():
                    if v['nombre'] == nombre and v.get('aula') == self.room:
                        codigo = v['codigo']
                        break
            # BUILD key_info for class (was missing!)
            if codigo:
                key_info = f'{codigo}_{int(index_y+6)}_{self.hours}_{days_es[index_x]}_{self.room}_0'
            else:
                key_info = self.key_info        

            if old_key in self.cl_info:
                self.cl_info[old_key]['dia'] = new_day
                self.cl_info[old_key]['hora_inicio'] = new_hour
                self.cl_info[old_key]['duracion'] = self.hours
                self.cl_info[old_key]['aula'] = self.room

            if key_info != old_key and old_key in self.cl_info:
                self.cl_info[key_info] = self.cl_info.pop(old_key)
                self.key_info = key_info
            else:
                self.key_info = old_key

            self.label.info_key = self.key_info    

            if self.key_info not in self.c_edited:
                self.c_edited.append(self.key_info)
            self.cell_to_edit['key'] = getattr(self.label, 'course_key', None)

            # Update occupancy: unregister from old slot and register into new
            old_slot = self._slot_key
            new_slot = (index_x, index_y,self.hours, self.type)
            if old_slot != new_slot:
                try:
                    self.unregister_from_slot(old_slot)
                except Exception as e:
                    print(f"Error in layout update: {e}")
                    pass
                # directly place will be handled by _update_slot_layout
                self.register_to_slot(self.label.winfo_x(), self.label.winfo_y())
            else:
                """# Cell hasn't moved - just reposition it properly without re-registering
                if index_x < 0 or index_y < 0: ##< Check if the label is moved out of the grid
                    self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y()) ##< Move the label back to the original position
                else:
                    # Trigger layout update for the current slot to ensure proper positioning
                    # but don't re-register (which would add duplicate entry)
                    self._update_slot_layout(new_slot)"""
                # Cell hasn't moved - but still need to update ALL overlapping widgets
                # in this day to ensure proper layout (not just this slot)
                self._update_all_overlapping_in_day(index_x, self.type)


        
        elif self.type == "lab": ##< Check if the label is a lab
            diff_x = [abs(x - self.label.winfo_x() + self.lab_displacement) for x in xlimit] ##< Get the difference between the x position of the label and the x positions of the grid, adding the lab displacement to the x position of the label
            index_x = diff_x.index(min(diff_x)) ##< Get the index of the minimum difference in the x axis. This gives the closest x (day) position in the grid to the label.
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit] ##< Get the difference between the y position of the label and the y positions of the grid
            index_y = diff_y.index(min(diff_y)) ##< Get the index of the minimum difference in the y axis. This gives the closest y (hour) position in the grid to the label.
            # print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00') ##< Print the position of the label when it is released
    
            # CLAMP index_y: Ensure label doesn't extend past grid bottom
            max_valid_index_y = len(ylimit) - self.hours
            if index_y > max_valid_index_y:
                index_y = max(0, max_valid_index_y)
            
            # Calculate the FINAL snapped position BEFORE any registration
            final_x = xlimit[index_x] + self.lab_displacement
            final_y = ylimit[index_y]

            # ALWAYS snap label to grid position after calculating/clamping indices
            self.label.place(x=final_x, y=final_y)
            # Force Tkinter to update the widget's position immediately
            self.label.update_idletasks()

            old_key = self.key_info
            nombre = self.label.cget("text").split("\n")[0]
            new_day = days_es[index_x]
            new_hour = int(index_y + 6)

            old_info = self.cl_info.get(old_key)
            if old_info:
                codigo = old_info['codigo']
            else:
                codigo = None
                for _, v in self.cl_info.items():
                    if v['nombre'] == nombre and v.get('aula') == self.room:
                        codigo = v['codigo']
                        break

            if codigo:
                key_info = f'{codigo}_{new_hour}_{self.hours}_{new_day}_{self.room}_1'
            else:
                key_info = old_key

            if old_key in self.cl_info:
                self.cl_info[old_key]['dia'] = new_day
                self.cl_info[old_key]['hora_inicio'] = new_hour
                self.cl_info[old_key]['duracion'] = self.hours
                self.cl_info[old_key]['aula'] = self.room

            if key_info != old_key and old_key in self.cl_info:
                self.cl_info[key_info] = self.cl_info.pop(old_key)
                self.key_info = key_info
            else:
                self.key_info = old_key

            self.label.info_key = self.key_info    

            if self.key_info not in self.c_edited:
                self.c_edited.append(self.key_info)

            self.cell_to_edit['key'] = getattr(self.label, 'course_key', None)
            
            # Update occupancy for lab similarly to class
            old_slot = self._slot_key
            new_slot = (index_x, index_y, self.hours, self.type)
            if old_slot != new_slot:
                try:
                    self.unregister_from_slot(old_slot)
                except Exception as e:
                    print(f"Error in layout update: {e}")
                    pass
                self.register_to_slot(self.label.winfo_x(), self.label.winfo_y())
            else:
                """# Cell hasn't moved - just reposition it properly without re-registering
                if index_x < 0 or index_y < 0: ##< Check if the label is moved out of the grid
                    self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y()) ##< Move the label back to the original position
                else:
                    # Trigger layout update for the current slot to ensure proper positioning
                    # but don't re-register (which would add duplicate entry)
                    self._update_slot_layout(new_slot)"""
                # Cell hasn't moved - but still need to update ALL overlapping widgets
                # in this day to ensure proper layout (not just this slot)
                self._update_all_overlapping_in_day(index_x, self.type)