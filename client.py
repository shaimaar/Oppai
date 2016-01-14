#############################################################
# FILE : ex10.py
# Writer #1: Shai Maarek , shaimaar , 305456261
# Writer #2: Oren Sultan, orens, 201557972
# DESCRIPTION: #todo
# Output: #todo
#############################################################

# todo before you assign this delete all print commands
############################################################
# Imports
############################################################
import sys
import socket
import re
import select
import tkinter as tki
from tkinter import *

############################################################
# Constants
############################################################

# sys arg parameters
SERVER_ADDRESS = 1
SERVER_PORT = 2
USER_NAME = 3
GROUP_NAME = 4
PARAMETERS_NUM = 5

TIME_LAPSE = 3000
MSG_TYPE = 0
MAX_CHAR_LEN = 20
TIMEOUT = 0.05
USER_NAME_LOC = 1
ERROR_MSG_LOC = 1
SHAPE_LOC = 2
SHAPE_COORD_LOC = 3
SHAPE_COLOR_LOC = 4

# canvas design
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
CANVAS_BACKGROUND = "white"
CANVAS_BORDER_WIDTH = 10

# for color buttons
RED = "red"
BLUE = "blue"
YELLOW = "yellow"
GREEN = "green"
BLACK = "black"
VIOLET = "violet"
ORANGE = "orange"

# for shape buttons
LINE = "line"
RECTANGLE = "rectangle"
CIRCLE = "oval"
TRIANGLE = "triangle"

DEFAULT_SHAPE = "line"
DEFAULT_COLOR = "blue"

# messages
ERROR_USER_NAME_MSG = 'Error. User name must be less than 20 characters'
ERROR_GROUP_NAME_MSG = 'Error. Group name must be less than 20 characters'
ERROR_BAD_CHARACTERS_MSG = 'Error. user name and group name must contain ' \
                           'numbers and English characters only'
ERROR_WRONG_PARAMETER_NUM = "Wrong number of parameters. The correct usage" \
                            "is:\npython client.py e-intro.cs.huji.ac.il " \
                            "8000,<user_name> <group_name>"
BUFFER_SIZE = 1024
MSG_DELIMITER = b'\n'



# todo - perheps make getters and setters to group_name, and user_name,
class DrawApp:
    def __init__(self, user_name, group_name, client_socket):
        self.root = tki.Tk()
        self.buttons_list = []
        self.clicks = []
        self.num_of_clicks = 0
        self.users_of_group = []
        self.cur_shape = DEFAULT_SHAPE
        self.cur_color = DEFAULT_COLOR

        self.colors_list = [RED, BLUE, YELLOW, GREEN, BLACK, VIOLET, ORANGE]
        self.shapes_list = [LINE, RECTANGLE, CIRCLE, TRIANGLE]

        # to present the name of the user_name on the window
        self.user_name = user_name
        self.root.title(user_name)
        self.group_name = group_name
        self.client_socket = client_socket

        self.color_label = Label(self.root, text="Choose a color")
        self.color_label.grid(row=1, column=0)

        self.shape_label = Label(self.root, text="Choose a shape")
        self.shape_label.grid(row=2, column=0)

        self.users_list_box = tki.Listbox(self.root, width=20, height=30)
        self.users_list_box.grid(row=3, column=0)

        self.create_help_menu()
        self.create_canvas()
        self.create_color_buttons()
        self.create_shape_buttons()

        # self.root.after(10,self)
        root = Tk()  # call the constructor of class to create blank window
        # put it in infinite loop, so the window will continuously be displayed till
        # will will press the exit button
        # todo call interact_with_server

        self.join_user_to_server()

        self.interact_with_server()


        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        root.mainloop()

    def on_closing(self):
        print("GoodBye")
        self.root.destroy()
        self.leave_client()
        self.client_socket.close()

    def create_help_menu(self):
        """
        Create help menu with instructions to the user
        :return:
        """
        menu = tki.Menu(self.root)
        help_menu = tki.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Instructions", command=self.instructions)
        self.root.config(menu=menu)

    @staticmethod
    def instructions():
        """
        Present to the user help instructions of the Application
        :return:
        """
        top = tki.Toplevel()
        top.title("instructions")
        msg = tki.Message(top, text="App Instructions: Hi, Please choose "
                                    "color and a shape by clicking the button,"
                                    "then click on the canvas."
                                    "3 clicks for triangle, and 2 "
                                    "clicks for other shapes.")
        msg.pack()

    @staticmethod
    def raise_error_msg(err_msg):
        """
        Present to the use the error message from server
        :param err_msg:
        :return:
        """
        top = tki.Toplevel()
        top.title("Error")
        msg = tki.Message(top, text=err_msg)
        msg.pack()

    def create_canvas(self):
        """
        Create the canvas with the defined width, height and border width
        Here the user will click.
        :return:
        """
        self.canvas = tki.Canvas(self.root, width=CANVAS_WIDTH,\
                                 height=CANVAS_HEIGHT,
                                 borderwidth=CANVAS_BORDER_WIDTH,
                                 bg=CANVAS_BACKGROUND, relief='raised')
        self.canvas.grid(row=3, column=1)
        self.canvas.bind("<Button-1>", self.click)

    def create_color_buttons(self):
        index = 2
        for color in self.colors_list:
            curr_color_button = tki.Button(text=color,command=
            self.command_color_buttons(color)).\
                grid(row=1, column=index, sticky=W)
            self.buttons_list.append(curr_color_button)
            index += 1

    def create_shape_buttons(self):
        index = 2
        for shape in self.shapes_list:
            curr_shape_button = tki.Button(text=shape, command=self.
                                           command_shape_buttons(shape))
            curr_shape_button.grid(row=2, column=index)
            self.buttons_list.append(curr_shape_button)
            index += 1

    def command_shape_buttons(self, shape):
        def change_cur_shape():
            self.clicks = []
            self.cur_shape = shape
        return change_cur_shape



    def command_color_buttons(self, color):
        def change_cur_color():
            self.clicks = []
            self.cur_color = color
        return change_cur_color

    def draw_shape(self, shape_tuple):
        """
        draw a shape in a specific color and position according to user
        :param shape_tuple:
        :return:
        """
        print('draw shape: ', str(shape_tuple))
        coords = shape_tuple[2].split(',')
        # if line
        if shape_tuple[1] == LINE:
            self.canvas.create_line(coords, fill=shape_tuple[3], width=3)
        # if rectangle
        elif shape_tuple[1] == RECTANGLE:
            self.canvas.create_rectangle(coords, fill=shape_tuple[3], width=3)
        # if circle
        elif shape_tuple[1] == CIRCLE:
            self.canvas.create_oval(coords, fill=shape_tuple[3], width=3)
        # if triangle
        else:
            self.canvas.create_polygon(coords, fill=shape_tuple[3],
                                       width=3)

        # draw text on the canvas shape
        self.canvas.create_text(coords[0], coords[1],
                                text=shape_tuple[0])

    def click(self,event):
        print('click: '+str(event.x)+','+str(event.y))
        self.clicks.append(event.x)
        self.clicks.append(event.y)
        self.num_of_clicks += 1
        if ((self.num_of_clicks == 2 and self.cur_shape != TRIANGLE) or
            (self.num_of_clicks == 3 and self.cur_shape == TRIANGLE)):
            self.add_shape(self.cur_shape,
                           self.clicks, self.cur_color)
            print("num of clicks: "+str(self.num_of_clicks)+ "shape: "+self.cur_shape)
            self.clicks = []
            self.num_of_clicks = 0

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
            self.users_of_group.append(name)
        self.update_users_list_box()

    def update_users_list_box(self):
        """
        update users_list_box by users of users_of_group list
        :return:
        """
        self.users_list_box.delete(0, tki.END)
        self.users_list_box.insert(tki.END, self.group_name)
        self.users_list_box.insert(tki.END, "users online:")
        for user in self.users_of_group:
            self.users_list_box.insert(tki.END, user)

    def interact_with_server(self):
        """
        Checks if a message was received using select, and transfers
        messages to
        functions
        that handle them.
        :return: None.
        """
        r, w, x = select.select([self.client_socket], [], [], TIMEOUT)
        for sock in r:
            if sock == self.client_socket:
                data = r[0].recv(BUFFER_SIZE)
                msg_list = data.decode('ascii').split('\n')
                for msg in msg_list:
                    parse_msg_list = msg.split(';')
                    self.handle_server_msgs(parse_msg_list[MSG_TYPE], parse_msg_list)
        self.root.after(TIME_LAPSE, self.interact_with_server)

    def join_user_to_server(self):
        """
        Joins new client to an existing or a new group.
        :return: None.
        """
        join_msg = bytes('join;' + user_name + ';' + group_name + '\n', 'ascii')
        self.client_socket.sendall(join_msg)

    def add_shape(self, shape_type, coordinates, color):
        """
        Sends the server the details of a new shape that drawn by the client
        :param shape_type: String representing the name of the shape: rectangle |
        | triangle | oval | line.
        :param coordinates: A list representing a list of coordinates
        :param color:
        :return: None
        """
        # convert list of int coordinated to string
        coordinates_str = ','.join(str(coord) for coord in coordinates)
        shape_msg = bytes('shape;' + shape_type + ';' + coordinates_str +
                          ';' + color + '\n', 'ascii')
        self.client_socket.sendall(shape_msg)

    def leave_client(self):
        """
        Informs server that client has ended the session
        :return: None.
        """
        leave_msg = bytes('leave\n', 'ascii')
        self.client_socket.sendall(leave_msg)

    def handle_server_msgs(self, msg_type, msg_list):
        """
         Handles server messages according to their type.
        :param msg_type: String representing the type of the message
        :param msg_list: List of message elements
        :return: None.
        """
        # Client joined existing group
        if msg_type == "join":
            joined_user_name = msg_list[USER_NAME_LOC]
            self.join_user(joined_user_name)
        # Shape was added
        elif msg_type == "shape":
            shape_user_name = msg_list[USER_NAME_LOC]
            shape_type = msg_list[SHAPE_LOC]
            shape_coordinates = msg_list[SHAPE_COORD_LOC]
            shape_color = msg_list[SHAPE_COLOR_LOC]
            shape_tuple = (shape_user_name, shape_type, shape_coordinates,
                           shape_color)
            self.draw_shape(shape_tuple)
        # A client left the group
        elif msg_type == "leave":
            quit_user_name = msg_list[USER_NAME_LOC]
            self.leave_user(quit_user_name)
        # All current users in group
        elif msg_type == "users":
            current_group_users = msg_list[USER_NAME_LOC].split(',')
            self.curr_group_users(current_group_users)
        # Error message
        elif msg_type == "error":
            error_msg = msg_list[ERROR_MSG_LOC]
            self.raise_error_msg(error_msg)

    def set_user_name(self, user_name):
        """
        Sets class user_name parameter to received parameter
        :param user_name: String representing user name
        :return: None.
        """
        self.user_name = user_name

    def set_group_name(self, group_name):
        """
        Sets class group_name parameter to received parameter
        :param group_name: String representing group name
        :return: None
        """
        self.group_name = group_name


    def get_user_name(self):
        """
        Returns the user name of the client
        :return: String representing the user name of the client
        """
        return self.user_name

    def get_group_name(self):
        """
        Returns the group name of the client
        :return: String representing the group name of the client
        """
        return self.group_name

    def get_scoket(self):
        """
        Returns the socket of the client
        :return: Socket type object
        """
        return self.client_socket


def legal_input(user_name, group_name):
    """
    Receives the user name and group name and checks if they're legal.
    :param user_name: String representing the user name
    :param group_name: String representing the group name
    :return: Boolean value - False if a parameter isn't legal, else returns
    True
    """
    if len(user_name) >= MAX_CHAR_LEN:
        print(ERROR_USER_NAME_MSG)
        return False
    elif len(group_name) >= MAX_CHAR_LEN:
        print(ERROR_GROUP_NAME_MSG)
        return False
    # Checks is user_name and group_name contain letters and numbers only
    elif re.match("^[A-Za-z0-9]*$", user_name) and re.match("^["
                                                            "A-Za-z0-9]*$",
                                                            group_name):
        return True
    else:
        print(ERROR_BAD_CHARACTERS_MSG)
        return False


if __name__ == '__main__':
    if len(sys.argv) != PARAMETERS_NUM:
        print(ERROR_WRONG_PARAMETER_NUM)
    elif legal_input(sys.argv[USER_NAME], sys.argv[GROUP_NAME]):
        server_address = sys.argv[SERVER_ADDRESS]
        server_port = sys.argv[SERVER_PORT]
        user_name = sys.argv[USER_NAME]
        group_name = sys.argv[GROUP_NAME]
        # create socket and connect to server
        client_socket = socket.socket()
        client_socket.connect((server_address, int(server_port)))
        # create new GUI object and connect to server
        gui_environment = DrawApp(user_name, group_name, client_socket)
        gui_environment.root.mainloop()
