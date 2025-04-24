from tkinter import *
from dnd import *

window = Tk()

window.attributes('-fullscreen', True)

screen_width = window.winfo_screenwidth()

screen_height = window.winfo_screenheight()

print(screen_width, screen_height)

single_width = int(0.0078125*screen_width)
double_width = 2*single_width

single_height = int(0.001389*screen_height)

# Add labels for hours
for hour in range(6, 22):
    label = Label(window, text=f"{hour}:00", bg="white", width=single_width, height=single_height, borderwidth=2, relief="raised")
    label.place(x=0, y=(hour-4)*25)
    ylimit.append((hour-4)*25)

# Add labels for days
for day in range(6):
    label = Label(window, text=days[day], bg="white", width=2*single_width, height=single_height, borderwidth=2, relief="raised")
    label.place(x=(day+1)*100+80*day, y=0)
    xlimit.append((day+1)*100+80*day)

# Add rooms and labs
for xl in xlimit:
    room = Label(window, text="Room", bg="white", width=single_width, height=single_height, borderwidth=2, relief="raised")
    room.place(x=xl, y=25*single_height)
    lab = Label(window, text="Lab", bg="white", width=single_width, height=single_height, borderwidth=2, relief="raised")
    lab.place(x=xl+88, y=25*single_height)

# Add classes
i = 0
for day in classes:
    j=0
    for cl in day:
        temp = cl.split("_")
        if temp[0]!='blank':
            dnd_label(window=window, geometry_width=screen_width, geometry_height=screen_height, text=temp[0], bg_color="gray", w=10, h=int(temp[1])+int(int(temp[1])*0.4), posx=xlimit[i], posy=(j+2)*25, hours=int(temp[1]), type="class")
        j+=int(temp[1])
    i+=1

# Add labs
i = 0
for day in labs:
    j=0
    for cl in day:
        temp = cl.split("_")
        if temp[0]!='blank':
            dnd_label(window=window, geometry_width=screen_width, geometry_height=screen_height, text=temp[0], bg_color="green", w=10, h=int(temp[1])+int(int(temp[1])*0.4), posx=xlimit[i]+90, posy=(j+2)*25, hours=int(temp[1]), type="lab")
        j+=int(temp[1])
    i+=1

window.mainloop()