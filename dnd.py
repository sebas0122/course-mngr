from tkinter import *

xlimit = [] ##< xlimit is to locate x positions of the labels in the grid
ylimit = [] ##< ylimit is to locate y positions of the labels in the grid

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] ##< days is to set the names of the days of the week
days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"] ##< days_es is to set the names of the days of the week in Spanish

# --- NEW: occupancy map to handle responsive widths when multiple items share a slot
slot_occupancy = {}  # key: (index_x, index_y, hours, type) -> list of Label widgets

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

## dnd_label class
#
# This class is used to create the Drag and Drop labels for the classes and labs in the schedule. It inherits from the Label class of tkinter.
# The class has the following methods:
# - __init__: This method is used to initialize the class. It takes the following parameters:
# - on_press: This method is used to get the position of the mouse when the label is pressed.
# - on_drag: This method is used to move the label when the mouse is dragged.
# - on_release: This method is used to check if the label is moved out of the window or the grid. If it is moved out of the window, it is moved back to the original position. If it is moved out of the grid, it is moved to the nearest position in the grid.
class dnd_label:

    ## The constructor.
    # It takes the following parameters:
    # @param window: The window where the label will be placed.
    # @param geometry_width: The width of the window.
    # @param geometry_height: The height of the window.
    # @param text: The text to be displayed in the label.
    # @param bg_color: The background color of the label.
    # @param w: The width of the label.
    # @param h: The height of the label.
    # @param posx: The x position of the label.
    # @param posy: The y position of the label.
    # @param hours: The number of hours the label will occupy in the grid.
    # @param type: The type of the label (class or lab).
    def __init__(self, window, image, geometry_width, geometry_height, lab_disp, text, bg_color, w, h, posx, posy, hours, type, room, info_label, cl_info, proffs_info, cell_to_edit, c_edited):
        self.geometry_x = geometry_width ##< The width of the window
        self.geometry_y = geometry_height ##< The height of the window
        self.lab_displacement = lab_disp ##< The displacement of the lab label in the x axis
        self.w = w ##< The width of the label
        self.h = h ##< The height of the label
        self.image = image

        self.label = Label(window,
                           image=image,
                           text=text,
                           font=("Arial", 7),
                           bg=bg_color,
                           width=w,
                           height=h,
                           wraplength=70,
                           relief="solid",
                           compound="center") ##< Create the label with the given parameters. The image is used to set the background of the label, the text is used to display the name of the class or lab, the bg_color is used to set the background color of the label, the width and height are used to set the size of the label, and the wraplength is used to set the maximum width of the text before it wraps to a new line.
        
        self.hours = hours ##< The number of hours the label will occupy in the grid
        self.type = type   ##< The type of the label (class or lab)
        self.room = room   ##< The room where the class/lab is held
        self.info_label = info_label ##< The label where the information of the course/lab will be displayed when the label is pressed
        self.cl_info = cl_info ##< The class information dictionary to be used in the info label
        self.proffs_info = proffs_info ##< The professors information dictionary to be used in the info label
        self.cell_to_edit = cell_to_edit ##< The cell to edit in the edit class window
        self.c_edited = c_edited ##< The edited classes keys
        self.label.place(x=posx, y=posy) ##< Set the position of the label
        self.label.bind("<Button-1>", self.on_press) ##< Bind the left mouse button to the on_press method
        self.label.bind("<B1-Motion>", self.on_drag) ##< Bind the left mouse button motion to the on_drag method
        self.label.bind("<ButtonRelease-1>", self.on_release) ##< Bind the left mouse button release to the on_release method

        # store initial pos and slot info
        self._initial_pos = (posx, posy)
        self._slot_key = None
        # register this widget into the occupancy map so layout can be computed responsively
        if xlimit and ylimit:
            try:
                self.register_to_slot(posx, posy)
            except Exception as e:
                print(f"Error in layout update: {e}")
                pass
    
     # --- NEW helpers for slot registration/layout ---
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

    def register_to_slot(self, posx=None, posy=None):
        # register label widget into slot_occupancy and trigger layout update
        if posx is None or posy is None:
            posx, posy = self.label.winfo_x(), self.label.winfo_y()
        slot = self._compute_slot_from_pos(posx, posy)
        if slot is None:
            return
        # ensure list exists and append if not present
        lst = slot_occupancy.setdefault(slot, [])
        # remove any stale or duplicate entries first
        lst = [w for w in lst if w.winfo_exists()]
        if self.label not in lst:
            lst.append(self.label)
        slot_occupancy[slot] = lst
        self._slot_key = slot
        self._update_slot_layout(slot)

    def unregister_from_slot(self, slot):
        if slot is None:
            return
        lst = slot_occupancy.get(slot, [])
        lst = [w for w in lst if w.winfo_exists() and w is not self.label]
        if lst:
            slot_occupancy[slot] = lst
            self._update_slot_layout(slot)
        else:
            slot_occupancy.pop(slot, None)
        if self._slot_key == slot:
            self._slot_key = None

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
                pass
    
    ## on_press method
    # This method is used to get the position of the mouse when the label is pressed.
    # It takes the following parameters:
    # @param event: The event that triggered the method.
    def on_press(self, event):
        self.x = event.x ##< Get the x position of the mouse
        self.y = event.y ##< Get the y position of the mouse

        # obscure this label's background and restore any previously obscured label
        prev = getattr(dnd_label, "active_label", None)
        if prev is not None and prev is not self:
            # restore previous label appearance
            try:
                prev.label.config(bg=getattr(prev, "_prev_bg", prev.label.cget("bg")), fg="black")
            except Exception as e:
                print(f"Error in layout update: {e}")
                pass

        if getattr(dnd_label, "active_label", None) is not self:
            # save current appearance so it can be restored later
            self._prev_bg = self.label.cget("bg")
            # obscure background: remove image and set a dark background color
            self.label.config(bg="#444444", fg="white")
            dnd_label.active_label = self

        nombre = self.label.cget("text") ##< Get the text of the label
        grupos = list(map(int, nombre.split("\n")[1].strip("[]").split(",")))
        print(f'Grupos: {grupos}')
        nombre = nombre.split("\n")[0] ##< Split the text to get only the name of the class/lab, without the group information

        key_info = f'{nombre}_{int(6+((self.label.winfo_y()-ylimit[0])/(ylimit[0]/2)))}_{self.hours}_{days_es[int((self.label.winfo_x()-xlimit[0])/(2*xlimit[0]))]}_{self.room}' ##< Create a key to access the class information
        print(f'on press: {key_info}') ##< Print the key info of the label being moved
        self.key_info = key_info ##< Create a key to access the class information
        self.cell_to_edit['key'] = key_info ##< Set the key of the cell to edit in the edit class window
        professors = [self.proffs_info[f'{id}']['name'] for id in self.cl_info[key_info]['profesor']] ##< Create an empty list to store the professors of the course/lab

        ## Shows in GUI the information of the course/lab being moved
        if(len(self.cl_info[key_info]['grupo'])>5):
            self.info_label.config(text=f"Código de materia: {self.cl_info[key_info]['codigo']}\t\t\t\tProfesores: {', '.join(professors)}\n\nGrupos: {', '.join(map(str, self.cl_info[key_info]['grupo']))}\t\t\t\tID Profesores: {', '.join(map(str, self.cl_info[key_info]['profesor']))}\n\nTipo de materia: {'Teoría' if self.type == 'class' else 'Laboratorio'}\t\t\t\tAula: {self.cl_info[key_info]['aula']}") ##< Set the text of the info label to the course code, groups, and professors of the label being moved
        else:
            self.info_label.config(text=f"Código de materia: {self.cl_info[key_info]['codigo']}\t\tProfesores: {', '.join(professors)}\n\nGrupos: {', '.join(map(str, self.cl_info[key_info]['grupo']))}\t\t\t\tID Profesores: {', '.join(map(str, self.cl_info[key_info]['profesor']))}\n\nTipo de materia: {'Teoría' if self.type == 'class' else 'Laboratorio'}\t\tAula: {self.cl_info[key_info]['aula']}") ##< Set the text of the info label to the course code, groups, and professors of the label being moved

    ## on_drag method
    # This method is used to move the label when the mouse is dragged.
    # It takes the following parameters:
    # @param event: The event that triggered the method.
    def on_drag(self, event):
        x = self.label.winfo_x() - self.x + event.x ##< Get the new x position of the label
        y = self.label.winfo_y() - self.y + event.y ##< Get the new y position of the label
        self.label.place(x=x, y=y) ##< Set the new position of the label. Keeps updating the position of the label as it is dragged.

    ## on_release method
    # This method is used to check if the label is moved out of the window or the grid. If it is moved out of the window, it is moved back to the original position. If it is moved out of the grid, it is moved to the nearest position in the grid.
    # It takes the following parameters:
    # @param event: The event that triggered the method.
    def on_release(self, event):
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
        elif self.label.winfo_y() + self.label.winfo_height() > self.geometry_y: ##< Check if the label is moved out of the window only in the y axis to the bottom
            self.label.place(x=self.label.winfo_x(), y=self.geometry_y - self.label.winfo_height()) ##< Move the label back to the original position in the y axis

        # Check if a label it is moved out of the grid
        if self.type == "class": ##< Check if the label is a class
            diff_x = [abs(x - self.label.winfo_x()) for x in xlimit] ##< Get the difference between the x position of the label and the x positions of the grid
            index_x = diff_x.index(min(diff_x)) ##< Get the index of the minimum difference in the x axis. This gives the closest x (day) position in the grid to the label.
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit] ##< Get the difference between the y position of the label and the y positions of the grid
            index_y = diff_y.index(min(diff_y)) ##< Get the index of the minimum difference in the y axis. This gives the closest y (hour) position in the grid to the label.
            # print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00') ##< Print the position of the label when it is released

            nombre = self.label.cget("text") ##< Get the text of the label
            nombre = nombre.split("\n")[0] ##< Split the text to get only the name of the class/lab, without the group information
            key_info = f'{nombre}_{int(index_y+6)}_{self.hours}_{days_es[index_x]}_{self.room}'

            if key_info != self.key_info: ##< Check if the key info of the label being moved is different from the key info of the label when it was pressed
                # print(f'on release: {key_info}') ##< Print the key info of the label being moved
                self.cl_info[key_info] = self.cl_info[self.key_info] ##< Update the class information dictionary with the new position of the label
                # print(f"Class info updated: {self.cl_info[key_info]}") ##< Print the class information
                del self.cl_info[self.key_info] ##< Delete the old position of the label from the class information
                self.c_edited.append(key_info) ##< Add the edited class key to the list
                self.c_edited.remove(self.key_info) if self.key_info in self.c_edited else None ##< Remove the old key info from the edited classes list
                # print(f"-------\nNew dictionary: {self.cl_info}\n-------") ##< Print the old key info of the label being moved

            # Update occupancy: unregister from old slot and register into new
            old_slot = self._slot_key
            new_slot = (index_x, index_y, self.hours, self.type)
            if old_slot != new_slot:
                try:
                    self.unregister_from_slot(old_slot)
                except Exception as e:
                    print(f"Error in layout update: {e}")
                    pass
                # directly place will be handled by _update_slot_layout
                self.register_to_slot(self.label.winfo_x(), self.label.winfo_y())
            else:
                if index_x < 0 or index_y < 0: ##< Check if the label is moved out of the grid
                    self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y()) ##< Move the label back to the original position
                else:
                    self.label.place(x=xlimit[index_x], y=ylimit[index_y]) ##< Move the label to the closest position in the grid. The y position is set to the ylimit list, which contains the y positions of the grid. The x position is set to the xlimit list, which contains the x positions of the grid.
        
        elif self.type == "lab": ##< Check if the label is a lab
            diff_x = [abs(x - self.label.winfo_x() + self.lab_displacement) for x in xlimit] ##< Get the difference between the x position of the label and the x positions of the grid, adding the lab displacement to the x position of the label
            index_x = diff_x.index(min(diff_x)) ##< Get the index of the minimum difference in the x axis. This gives the closest x (day) position in the grid to the label.
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit] ##< Get the difference between the y position of the label and the y positions of the grid
            index_y = diff_y.index(min(diff_y)) ##< Get the index of the minimum difference in the y axis. This gives the closest y (hour) position in the grid to the label.
            # print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00') ##< Print the position of the label when it is released

            nombre = self.label.cget("text") ##< Get the text of the label
            nombre = nombre.split("\n")[0] ##< Split the text to get only the name of the class/lab, without the group information
            key_info = f'{nombre}_{int(index_y+6)}_{self.hours}_{days_es[index_x]}_{self.room}'

            if key_info != self.key_info: ##< Check if the key info of the label being moved is different from the key info of the label when it was pressed
                # print(f'on release: {key_info}') ##< Print the key info of the label being moved
                self.cl_info[key_info] = self.cl_info[self.key_info] ##< Update the class information dictionary with the new position of the label
                # print(f"Class info updated: {self.cl_info[key_info]}") ##< Print the class information
                del self.cl_info[self.key_info] ##< Delete the old position of the label from the class information
                self.c_edited.append(key_info) ##< Add the edited class key to the list
                self.c_edited.remove(self.key_info) if self.key_info in self.c_edited else None ##< Remove the old key info from the edited classes list
                # print(f"-------\nNew dictionary: {self.cl_info}\n-------") ##< Print the old key info of the label being moved
            
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
                if index_x < 0 or index_y < 0: ##< Check if the label is moved out of the grid
                    self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y()) ##< Move the label back to the original position
                else:
                    self.label.place(x=xlimit[index_x]+self.lab_displacement, y=ylimit[index_y]) ##< Move the label to the closest position in the grid. The y position is set to the ylimit list, which contains the y positions of the grid. The x position is set to the xlimit list, which contains the x positions of the grid, adding the lab displacement to the x position of the label.