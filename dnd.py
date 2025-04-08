from tkinter import *

xlimit = []
ylimit = []
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
# class_hours, hours must add 16
classes = [
    ["class2_2", "blank_2", "class3_3", "blank_5", "class4_4"],
    ["class2_2", "class2_2", "blank_4", "class_2"],
    ["class2_2", "blank_2", "class4_4", "class3_3", "blank_2", "class3_3"],
    ["class2_2", "class2_2", "blank_4", "class_2"],
    ["class5_5", "blank_5", "class6_6"],
    ["class2_2"],
]

labs = [
    ["lab3_3", "blank_6", "lab3_3", "lab2_2"],
    ["blank_2", "lab3_3", "lab3_3", "lab3_3"],
    ["blank_4", "lab3_3", "lab3_3"],
    ["blank_2", "lab3_3", "lab3_3", "lab3_3"],
    ["lab3_3", "blank_6", "lab3_3", "lab2_2"],
    ["blank_4", "lab2_2"],
]

class dnd_label:
    def __init__(self, window, geometry):
        self.window = window
        self.geometry_x = geometry[0]
        self.geometry_y = geometry[1]

    def add_label(self, text, bg_color, w, h, posx, posy, hours):
        self.label = Label(self.window, text=text, bg=bg_color, width=w, height=h, borderwidth=2, relief="raised")
        self.hours = hours
        self.label.place(x=posx, y=posy)
        self.label.bind("<Button-1>", self.on_press)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<ButtonRelease-1>", self.on_release)
    
    def on_press(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        x = self.label.winfo_x() - self.x + event.x
        y = self.label.winfo_y() - self.y + event.y
        self.label.place(x=x, y=y)

    def on_release(self, event):
        print("on_release: x=%d, y=%d" % (self.label.winfo_x(), self.label.winfo_y()))

        # Check if it is moved out of the window
        if self.label.winfo_x() < 0 and self.label.winfo_y() < 0:
            self.label.place(x=0, y=0)
        elif self.label.winfo_x() < 0:
            self.label.place(x=0, y=self.label.winfo_y())
        elif self.label.winfo_y() < 0:
            self.label.place(x=self.label.winfo_x(), y=0)

        # Check if it is moved out of the window
        if self.label.winfo_x() + self.label.winfo_width() > self.geometry_x and self.label.winfo_y() + self.label.winfo_height() > self.geometry_y:
            self.label.place(x=self.geometry_x - self.label.winfo_width(), y=self.geometry_y - self.label.winfo_height())
        elif self.label.winfo_x() + self.label.winfo_width() > self.geometry_x:
            self.label.place(x=self.geometry_x - self.label.winfo_width(), y=self.label.winfo_y())
        elif self.label.winfo_y() + self.label.winfo_height() > self.geometry_y:
            self.label.place(x=self.label.winfo_x(), y=self.geometry_y - self.label.winfo_height())

        # Check if it is moved out of the grid
        diff_x = [abs(x - self.label.winfo_x()) for x in xlimit]
        index_x = diff_x.index(min(diff_x))
        diff_y = [abs(y - self.label.winfo_y()) for y in ylimit]
        index_y = diff_y.index(min(diff_y))
        print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00')
        if index_x < 0 or index_y < 0:
            self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y())
        else:
            self.label.place(x=xlimit[index_x], y=ylimit[index_y])