from tkinter import *

geometry_x = 1200
geometry_y = 600

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
    def __init__(self, text, bg_color, w, h, posx, posy, hours, type):
        self.label = Label(window, text=text, bg=bg_color, width=w, height=h, borderwidth=2, relief="raised")
        self.hours = hours
        self.type = type
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
        if self.label.winfo_x() + self.label.winfo_width() > geometry_x and self.label.winfo_y() + self.label.winfo_height() > geometry_y:
            self.label.place(x=geometry_x - self.label.winfo_width(), y=geometry_y - self.label.winfo_height())
        elif self.label.winfo_x() + self.label.winfo_width() > geometry_x:
            self.label.place(x=geometry_x - self.label.winfo_width(), y=self.label.winfo_y())
        elif self.label.winfo_y() + self.label.winfo_height() > geometry_y:
            self.label.place(x=self.label.winfo_x(), y=geometry_y - self.label.winfo_height())

        # Check if it is moved out of the grid
        if self.type == "class":
            diff_x = [abs(x - self.label.winfo_x()) for x in xlimit]
            index_x = diff_x.index(min(diff_x))
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit]
            index_y = diff_y.index(min(diff_y))
            print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00')
            if index_x < 0 or index_y < 0:
                self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y())
            else:
                self.label.place(x=xlimit[index_x], y=ylimit[index_y])
        elif self.type == "lab":
            diff_x = [abs(x - self.label.winfo_x()) for x in xlimit]
            index_x = diff_x.index(min(diff_x))
            diff_y = [abs(y - self.label.winfo_y()) for y in ylimit]
            index_y = diff_y.index(min(diff_y))
            print(f'Class {self.label.cget("text")} moved to {days[index_x]} at {index_y+6}:00 to {index_y+6+self.hours}:00')
            if index_x < 0 or index_y < 0:
                self.label.place(x=self.label.winfo_x(), y=self.label.winfo_y())
            else:
                self.label.place(x=xlimit[index_x]+90, y=ylimit[index_y])

window = Tk()

window.geometry(f"{geometry_x}x{geometry_y}")
but = Button(command=window.quit, text="Quit")
but.place(x=0, y=0)

# Add labels for hours
for hour in range(6, 22):
    label = Label(window, text=f"{hour}:00", bg="white", width=10, height=1, borderwidth=2, relief="raised")
    label.place(x=0, y=(hour-4)*25)
    ylimit.append((hour-4)*25)

# Add labels for days
for day in range(6):
    label = Label(window, text=days[day], bg="white", width=21, height=1, borderwidth=2, relief="raised")
    label.place(x=(day+1)*100+80*day, y=0)
    xlimit.append((day+1)*100+80*day)

# Add rooms and labs
for xl in xlimit:
    room = Label(window, text="Room", bg="white", width=10, height=1, borderwidth=2, relief="raised")
    room.place(x=xl, y=25)
    lab = Label(window, text="Lab", bg="white", width=10, height=1, borderwidth=2, relief="raised")
    lab.place(x=xl+88, y=25)

# Add classes
i = 0
for day in classes:
    j=0
    for cl in day:
        temp = cl.split("_")
        if temp[0]!='blank':
            dnd_label(text=temp[0], bg_color="gray", w=10, h=int(temp[1])+int(int(temp[1])*0.4), posx=xlimit[i], posy=(j+2)*25, hours=int(temp[1]), type="class")
        j+=int(temp[1])
    i+=1

# Add labs
i = 0
for day in labs:
    j=0
    for cl in day:
        temp = cl.split("_")
        print(temp)
        if temp[0]!='blank':
            dnd_label(text=temp[0], bg_color="green", w=10, h=int(temp[1])+int(int(temp[1])*0.4), posx=xlimit[i]+90, posy=(j+2)*25, hours=int(temp[1]), type="lab")
        j+=int(temp[1])
    i+=1

window.mainloop()