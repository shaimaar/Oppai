import tkinter as tki
from tkinter import *

# canvas design
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
CANVAS_BACKGROUND = "white"

# for color buttons
RED = "Red"
BLUE = "Blue"
YELLOW = "Yellow"
GREEN = "Green"
BLACK = "Black"
VIOLET = "Violet"
ORANGE = "Orange"

# for shape buttons
LINE = "line"
RECTANGLE = "rectangle"
CIRCLE = "oval"
TRIANGLE = "triangle"

class DrawApp:
    def __init__(self, username):
        self.root = tki.Tk()
        self.buttons_list = []
        self.users_of_group = []

        self.colors_list = [RED, BLUE, YELLOW, GREEN, BLACK, VIOLET, ORANGE]
        self.shapes_list = [LINE, RECTANGLE, CIRCLE, TRIANGLE]

        # to present the name of the username on the window
        self.username = username
        self.root.title(username)

        self.help_button = tki.Button(text="Help").grid(row=0, column=0)
        self.color_label = Label(self.root, text="Choose a color")
        self.color_label.grid(row=1, column=0)

        self.shape_label = Label(self.root, text="Choose a shape")
        self.shape_label.grid(row=2, column=0)

        self.users_list_box = tki.Listbox()
        self.users_list_box.grid(row=2, column=0)

        self.create_canvas()
        self.build_color_buttons()
        self.build_shape_buttons()


        # self.root.after(10,self)
        root = Tk()  # call the constructor of class to create blank window
        # put it in infinite loop, so the window will continuously be displayed till
        # will will press the exit button
        root.mainloop()


    def create_canvas(self):
        self.canvas = tki.Canvas(self.root, width=CANVAS_WIDTH,\
                                 height=CANVAS_HEIGHT, bg=CANVAS_BACKGROUND)
        self.canvas.grid(row=3, column=1)
        self.canvas.bind("<Button-1>", self.click)

    def build_color_buttons(self):
        index = 2
        for color in self.colors_list:
            curr_color_button = tki.Button(text=color)
            curr_color_button.grid(row=1, column=index)
            curr_color_button.config(height=20, width=10)
            self.buttons_list.append(curr_color_button)
            index += 1

    def build_shape_buttons(self):
        index = 2
        for color in self.shapes_list:
            curr_shape_button = tki.Button(text=color)
            curr_shape_button.grid(row=2, column=index)
            curr_shape_button.config(height=20, width=10)
            self.buttons_list.append(curr_shape_button)
            index += 1

    def draw_shape(self, shape_tuple):
        """
        draw a shape in a specific color and position according to user
        :param shape_tuple:
        :return:
        """
        # if line
        if shape_tuple[1] == LINE:
            self.canvas.create_line(shape_tuple[2], fill=shape_tuple[3],
                                    width=3)
        # if rectangle
        elif shape_tuple[1] == RECTANGLE:
            self.canvas.create_rectangle(shape_tuple[2],fill=shape_tuple[3],
                                         width=3)
        # if circle
        elif shape_tuple[1] == CIRCLE:
            self.canvas.create_oval(shape_tuple[2], fill=shape_tuple[3],
                                    width=3)
        # if triangle
        else:
            self.canvas.create_polygon(shape_tuple[2],fill=shape_tuple[3],
                                       width=3, outline="black")

        # draw text on the canvas shape
        self.canvas.create_text(shape_tuple[2][0], shape_tuple[2][1],
                                text=shape_tuple[0])

    def click(self,event):
        self.clicks.append((event.x,event.y))
        if len(self.clicks) == 2 and self.cur_shape != TRIANGLE:
            self.send_shape_msg()
            self.clicks.clear()
        if len(self.clicks) == 3 and self.cur_shape == TRIANGLE:
            self.send_shape_msg()
            self.clicks.clear()

    def join_user(self, user_name):
        """
        add user to users_of_group list
        call update_users_list_box, so we will see the update on screen
        :param user_name:
        :return:
        """
        self.users_of_group.append(user_name)
        self.update_users_list_box()

    def leave_user(self, user_name):
        """
        remove the user from users_of_group list if he left
        call update_users_list_box, so we will see the update on screen
        :param user_name:
        :return:
        """
        if user_name in self.users_of_group:
            self.users_of_group.remove(user_name)
        self.update_users_list_box()

    def curr_group_users(self, curr_group):
        """
        add all of the other users (except the user of the client)
        to users_of_group list.
        call update_userts_list_box, so we will see the update on screen
        :param curr_group:
        :return:
        """
        # run all of the names of users in the group
        for name in curr_group:
            # add the other users to the group
            if name != self.username:
                self.users_of_group.append(name)
        self.update_users_list_box()

    def update_users_list_box(self):
        """
        update users_list_box by users of users_of_group list
        :return:
        """
        for user in self.users_of_group:
            self.users_list_box.insert(0, user)

if __name__ == "__main__" :

    D = DrawApp('oren')





