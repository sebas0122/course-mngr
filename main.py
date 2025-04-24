from tkinter import *
from dnd import *

window = Tk() ##< Create a window

window.attributes('-fullscreen', True) ##< Set the window to fullscreen

screen_width = window.winfo_screenwidth() ##< Get the screen width

screen_height = window.winfo_screenheight() ##< Get the screen height

quit_button = Button(window, text="Quit", background="red", command=window.quit) ##< Create a quit button
quit_button.place(x=screen_width-50, y=0) ##< Set the position of the quit button

single_width = int(0.0078125*screen_width) ##< Set the width of a single cell
single_height = int(0.001389*screen_height) ##< Set the height of a single cell

# Add cells for hours
for hour in range(6, 22):
    label = Label(window, text=f"{hour}:00", bg="white", width=single_width, height=single_height, borderwidth=2, relief="raised")
    if hour == 6:
        label.place(x=0, y=(hour-4)*26) ##< Set the first label at 6:00
        ylimit.append((hour-4)*26)      ##< Add the position to the ylimit list
    else:
        label.place(x=0, y=(hour-4)*27) ##< Set the rest of the labels at 7:00 and above
        ylimit.append((hour-4)*27)      ##< Add the position to the ylimit list

# Add labels for days
for day in range(6):
    label = Label(window, text=days[day], bg="white", width=int(2.3*single_width), height=single_height, borderwidth=2, relief="raised")
    label.place(x=(day+1)*100+80*day, y=0) ##< Set the label position
    xlimit.append((day+1)*100+80*day)      ##< Add the position to the xlimit list

# Add rooms and labs in use each day each hour by semester
for xl in xlimit:
    room = Label(window, text="Room", bg="white", width=single_width, height=single_height, borderwidth=2, relief="raised")
    room.place(x=xl, y=25*single_height) ##< Set the label position
    lab = Label(window, text="Lab", bg="white", width=single_width, height=single_height, borderwidth=2, relief="raised")
    lab.place(x=xl+lab_displacement, y=25*single_height) ##< Set the label position

# Add classes (rooms) to schedule
i = 0 ##< Initialize the index for xlimit
for day in classes: ##< Iterate over the classes
    j=0 ##< Initialize the index for ylimit
    for cl in day:
        temp = cl.split("_") ##< Split the string to get the class name and hours
        if temp[0]!='blank': ##< Check if the class is not blank (free space)
            dnd_label(window=window, geometry_width=screen_width, geometry_height=screen_height, text=temp[0], bg_color="gray", w=single_width, h=cell_h.get(int(temp[1])), posx=xlimit[i], posy=ylimit[j], hours=int(temp[1]), type="class") ##< Create the drag&drop label for the class
        j+=int(temp[1]) ##< Increment the index for ylimit by the number of hours of the class
    i+=1 ##< Increment the index for xlimit by 1

# Add labs to schedule
i = 0 ##< Initialize the index for xlimit
for day in labs: ##< Iterate over the labs
    j=0 ##< Initialize the index for ylimit
    for cl in day: 
        temp = cl.split("_") ##< Split the string to get the lab name and hours
        if temp[0]!='blank': ##< Check if the lab is not blank (free space)
            dnd_label(window=window, geometry_width=screen_width, geometry_height=screen_height, text=temp[0], bg_color="green", w=single_width, h=cell_h.get(int(temp[1])), posx=xlimit[i]+lab_displacement, posy=ylimit[j], hours=int(temp[1]), type="lab") ##< Create the drag&drop label for the lab
        j+=int(temp[1]) ##< Increment the index for ylimit by the number of hours of the lab
    i+=1 ##< Increment the index for xlimit by 1

window.mainloop() ##< Start the main loop of the window