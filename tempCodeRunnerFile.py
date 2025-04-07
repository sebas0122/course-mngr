from tkinter import *

geometry_x = 800
geometry_y = 600
padding_factor = 0.001
unit_cell_factor_x = 0.008
unit_cell_factor_y = 0.008

# Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
# class_hours, hours must add 16
classes = [
    ["class1_2", "class2_2", "class3_12"],
    ["class1_1", "class2_1", "class3_14"],
    ["class1_3", "class2_3", "class3_13"],
    ["class1_4", "class2_4", "class3_8"],
    ["class1_5", "class2_5", "class3_6"],
    ["class1_6", "class2_6", "class3_4"],
    
]

class dnd_label:
    def __init__(self, text, bg_color, w, h, posx, posy):
        self.label = Label(window, text=text, bg=bg_color, width=w, height=h)
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

def insert_ver_divider(window, x, y, w, h):
    label = Label(window, width=w, height=h, bg="black")
    label.place(x=x, y=y)
    label.pack()

def insert_hor_divider(canvas, x, y, w, h):
    canvas.create_line(x, y, w, h, fill="black")

window = Tk()

window.geometry(f"{geometry_x}x{geometry_y}")
but = Button(command=window.quit, text="Quit")
but.place(x=0, y=0)


# Draw schedule's hours
w = int(window.winfo_width() * unit_cell_factor_x)
h = int(window.winfo_height() * unit_cell_factor_y)
print(w,h)

# Add labels for hours
for hour in range(6, 22):
    label = Label(window, text=f"{hour}:00", bg="white", width=10, height=1, borderwidth=2, relief="raised")
    label.place(x=0, y=(hour-4)*25)

# Add labels for days
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
for day in range(6):
    label = Label(window, text=days[day], bg="white", width=10, height=1)
    label.place(x=(day+1)*100, y=0)

# Add classes
i = 0
for day in classes:
    j=0
    for cl in day:
        temp = cl.split("_")
        dnd_label(temp[0], "red", 10, int(temp[1]), (i+1)*100, (j+2)*25)
        j+=int(temp[1])
    i+=1

window.mainloop()