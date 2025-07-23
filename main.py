from tkinter import *
from tkinter import ttk
from dnd import *
from courses_functions import connectSQL, getClassesList, getProfessorsData

dataframe = connectSQL("materias") ##< Connect to the database and get the data

window = Tk() ##< Create a window

window.attributes('-fullscreen', True) ##< Set the window to fullscreen

screen_width = window.winfo_screenwidth() ##< Get the screen width
print("Screen width:", screen_width) ##< Print the screen width

screen_height = window.winfo_screenheight() ##< Get the screen height
print("Screen height:", screen_height) ##< Print the screen height

pixel = PhotoImage(width=1, height=1)

quit_button = Button(window, text="Quit", background="red", command=window.quit) ##< Create a quit button
quit_button.place(x=int(screen_width*(14/15)), y=0) ##< Set the position of the quit button

single_width = int(screen_width / 15) ##< Set the width of a single cell
single_height = int(screen_height / 30) ##< Set the height of a single cell

lab_displacement = int(2*single_width)-single_width ##< lab_displacement is to set the displacement of the labs cells in the grid (compared to the rooms). This is done to avoid overlapping with the rooms and avoid creating another xlimit list. The value is how many pixels is moved to the right.

# Add cells for hours
for hour in range(6, 22):
    label = Label(window,
                  image=pixel,
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
                          font=("Arial", 16),
                          justify="left",
                          bg="#DECCCC",
                          image=pixel,
                          height=screen_height - (ylimit[-1]+2*single_height),
                          width=screen_width,
                          compound="center") ##< Create a label for the test
information_label.place(x=0, y=ylimit[-1]+3*single_height) ##< Set the rest of the labels at 7:00 and above

# Add labels for days
for day in range(6):
    label = Label(window,
                  image=pixel,
                  text=days[day],
                  width=2*single_width-4,
                  height=single_height-4,
                  compound="center") ##< Create a label for each day
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
                 text="Room",
                 width=single_width-4,
                 height=single_height-4,
                 compound="center") ##< Create a label for the room
    room.place(x=xl, y=single_height) ##< Set the label position
    
    lab = Label(window,
                image=pixel,
                text="Lab",
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

## add_classes_labs function
# This function adds classes and labs to the schedule. It takes the following parameters:
# - classes: a list of classes for each day
# - labs: a list of labs for each day
# Returns:
# - labels_ids: a list of labels ids for the classes and labs added to the schedule
def add_classes_labs(classes, labs, cl_information_label, lb_information_label):
    labels_ids = [] ##< Initialize the list of labels ids
    # Add classes (rooms) to schedule
    i = 0 ##< Initialize the index for xlimit
    for day in classes: ##< Iterate over the classes
        j=0 ##< Initialize the index for ylimit
        for cl in day:
            temp = cl.split("_") ##< Split the string to get the class name and hours
            if temp[0]!='blank': ##< Check if the class is not blank (free space)

                dnd_label(window=window,
                          image=pixel,
                          geometry_width=screen_width,
                          geometry_height=screen_height,
                          lab_disp=0,
                          text=temp[0],
                          bg_color="#B89E97",
                          w=single_width-4,
                          h=(int(temp[1])*single_height)-4,
                          posx=xlimit[i],
                          posy=ylimit[j],
                          hours=int(temp[1]),
                          type="class",
                          info_label=information_label,
                          cl_info=cl_information_label) ##< Create the drag&drop label for the class

                labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
            j+=int(temp[1]) ##< Increment the index for ylimit by the number of hours of the class
        i+=1 ##< Increment the index for xlimit by 1

    # Add labs to schedule
    i = 0 ##< Initialize the index for xlimit
    for day in labs: ##< Iterate over the labs
        j=0 ##< Initialize the index for ylimit
        for cl in day: 
            temp = cl.split("_") ##< Split the string to get the lab name and hours
            if temp[0]!='blank': ##< Check if the lab is not blank (free space)

                dnd_label(window=window,
                          image=pixel,
                          geometry_width=screen_width,
                          geometry_height=screen_height,
                          lab_disp=lab_displacement,
                          text=temp[0],
                          bg_color="#4ECDC4",
                          w=single_width-4,
                          h=(int(temp[1])*single_height)-4,
                          posx=xlimit[i]+lab_displacement,
                          posy=ylimit[j],
                          hours=int(temp[1]),
                          type="lab",
                          info_label=information_label,
                          cl_info=lb_information_label) ##< Create the drag&drop label for the lab

                labels_ids.append(window.winfo_children()[-1]) ##< Append the label id to the list
            j+=int(temp[1]) ##< Increment the index for ylimit by the number of hours of the lab
        i+=1 ##< Increment the index for xlimit by 1

    return labels_ids ##< Return the list of labels ids

c, l, c_info, l_info = getClassesList(dataframe, 1) ##< Get the classes and labs for level 1
lbs_ids = add_classes_labs(c, l, c_info, l_info) ##< Call the function to add classes and labs to the schedule

# Add dropdown menu for level selection

## change_level function
# This function is called when the user selects a level from the dropdown menu. It updates the schedule with the classes and labs for the selected level.
# It takes no parameters and returns nothing because it modifies the global variable lbs_ids.
def change_level():
    global lbs_ids
    lbl.config(text=opt.get())

    # Destroy all dnd_labels
    for widget in window.winfo_children():
        if len(lbs_ids) == 0:
            break
        if isinstance(widget, Label):
            if widget == lbs_ids[0]:
                lbs_ids.remove(widget) ##< Remove the label id from the list
                widget.destroy()

    # Add classes and labs to the schedule based on the selected level
    if opt.get() == "Level 1":
        c, l, c_info, l_info = getClassesList(dataframe, 1) ##< Call the function to add classes and labs to the schedule
    elif opt.get() == "Level 2":
        c, l, c_info, l_info = getClassesList(dataframe, 2) ##< Call the function to add classes and labs to the schedule
    elif opt.get() == "Level 3":
        c, l, c_info, l_info = getClassesList(dataframe, 3)
    elif opt.get() == "Level 4":
        c, l, c_info, l_info = getClassesList(dataframe, 4)
    elif opt.get() == "Level 5":
        c, l, c_info, l_info = getClassesList(dataframe, 5)
    elif opt.get() == "Level 6":
        c, l, c_info, l_info = getClassesList(dataframe, 6)
    elif opt.get() == "Level 7":
        c, l, c_info, l_info = getClassesList(dataframe, 7)
    elif opt.get() == "Level 8":
        c, l, c_info, l_info = getClassesList(dataframe, 8)
    elif opt.get() == "Level 9":
        c, l, c_info, l_info = getClassesList(dataframe, 9)
    lbs_ids = add_classes_labs(c, l, c_info, l_info)

# Dropdown options
level = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9"] 

# Selected option variable  
opt = StringVar(value="Level 1")

# Dropdown menu  
dd_menu = OptionMenu(window, opt, *level)
dd_menu.place(x=int(screen_width*(14/15)), y=int(screen_height/12)) ##< Set the position of the quit button

# Button to update label  
dd_button = Button(window, text="Aceptar", command=change_level)
dd_button.place(x=int(screen_width*(14/15)), y=int(screen_height/8)) ##< Set the position of the quit button

lbl = Label(window, text=" ")  
lbl.place(x=int(screen_width*(14/15)), y=int(screen_height/6)) ##< Set the position of the quit button

window.mainloop() ##< Start the main loop of the window