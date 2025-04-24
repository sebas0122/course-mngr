from tkinter import *

xlimit = [] ##< xlimit is to locate x positions of the labels in the grid
ylimit = [] ##< ylimit is to locate y positions of the labels in the grid

cell_h = {1: 0, 2: 3, 3: 5, 4: 6, 5: 8, 6: 10} ##< cell_h is to set the height of the labels in the grid, where the key is the number of hours and the value is the height in pixels

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] ##< days is to set the names of the days of the week

classes = [
    ["class2_2", "blank_2", "class3_3", "blank_5", "class4_4"],
    ["class2_2", "class2_2", "blank_4", "class_2"],
    ["class2_2", "blank_2", "class4_4", "class3_3", "blank_2", "class3_3"],
    ["class2_2", "class2_2", "blank_4", "class2_2"],
    ["class5_5", "blank_5", "class6_6"],
    ["class2_2", "blank_5", "class1_1"],
] ##< classes contains the classes for each day of the week, coded as <class name>_<number of hours>. The blank elements are used to create free space in the grid. First list is Monday, second is Tuesday, and so on. The number of hours must add maximum 16, which is the total number of hours in the schedule.

labs = [
    ["lab3_3", "blank_6", "lab3_3", "lab2_2"],
    ["blank_2", "lab3_3", "lab3_3", "lab3_3"],
    ["blank_4", "lab3_3", "lab3_3"],
    ["blank_2", "lab3_3", "lab3_3", "lab3_3"],
    ["lab3_3", "blank_6", "lab3_3", "lab2_2"],
    ["blank_4", "lab2_2", "lab1_1"],
] ##< labs contains the labs for each day of the week, coded as <lab name>_<number of hours>. The blank elements are used to create free space in the grid. First list is Monday, second is Tuesday, and so on. The number of hours must add maximum 16, which is the total number of hours in the schedule.

lab_displacement = 91 ##< lab_displacement is to set the displacement of the labs cells in the grid (compared to the rooms). This is done to avoid overlapping with the rooms and avoid creating another xlimit list. The value is how many pixels is moved to the right.

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
    def __init__(self, window, geometry_width, geometry_height, text, bg_color, w, h, posx, posy, hours, type):
        self.geometry_x = geometry_width ##< The width of the window
        self.geometry_y = geometry_height ##< The height of the window

        self.label = Label(window, text=text, bg=bg_color, width=w, height=h, borderwidth=2, relief="raised") ##< Create the label
        self.hours = hours ##< The number of hours the label will occupy in the grid
        self.type = type   ##< The type of the label (class or lab)
        self.label.place(x=posx, y=posy) ##< Set the position of the label
        self.label.bind("<Button-1>", self.on_press) ##< Bind the left mouse button to the on_press method
        self.label.bind("<B1-Motion>", self.on_drag) ##< Bind the left mouse button motion to the on_drag method
        self.label.bind("<ButtonRelease-1>", self.on_release) ##< Bind the left mouse button release to the on_release method
    
    ## on_press method
    # This method is used to get the position of the mouse when the label is pressed.
    # It takes the following parameters:
    # @param event: The event that triggered the method.
    def on_press(self, event):
        self.x = event.x ##< Get the x position of the mouse
        self.y = event.y ##< Get the y position of the mouse
    
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
            print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00') ##< Print the position of the label when it is released
            if index_x < 0 or index_y < 0: ##< Check if the label is moved out of the grid
                self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y()) ##< Move the label back to the original position
            else:
                self.label.place(x=xlimit[index_x], y=ylimit[index_y]) ##< Move the label to the closest position in the grid. The y position is set to the ylimit list, which contains the y positions of the grid. The x position is set to the xlimit list, which contains the x positions of the grid.
        
        elif self.type == "lab": ##< Check if the label is a lab
            diff_x = [abs(x - self.label.winfo_x() + lab_displacement) for x in xlimit] ##< Get the difference between the x position of the label and the x positions of the grid, adding the lab displacement to the x position of the label
            index_x = diff_x.index(min(diff_x)) ##< Get the index of the minimum difference in the x axis. This gives the closest x (day) position in the grid to the label.
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit] ##< Get the difference between the y position of the label and the y positions of the grid
            index_y = diff_y.index(min(diff_y)) ##< Get the index of the minimum difference in the y axis. This gives the closest y (hour) position in the grid to the label.
            print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00') ##< Print the position of the label when it is released
            if index_x < 0 or index_y < 0: ##< Check if the label is moved out of the grid
                self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y()) ##< Move the label back to the original position
            else:
                self.label.place(x=xlimit[index_x]+lab_displacement, y=ylimit[index_y]) ##< Move the label to the closest position in the grid. The y position is set to the ylimit list, which contains the y positions of the grid. The x position is set to the xlimit list, which contains the x positions of the grid, adding the lab displacement to the x position of the label.