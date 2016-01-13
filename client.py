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

SERVER_ADDRESS = 1
SERVER_PORT = 2
USER_NAME = 3
GROUP_NAME = 4
PARAMETERS_NUM = 5

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








def legal_input(user_name, group_name):
    """
    Receives the user name and group name and checks if they're legal.
    :param user_name: String representing the user name
    :param group_name: String representing the group name
    :return: Boolean value - False if a parameter isn't legal, else returns
    True
    """
    if len(user_name) >= 20:
        print(ERROR_USER_NAME_MSG)
        return False
    elif len(group_name) >= 20:
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


def connect_to_server():
    # todo documentation
    pass


def join_user(socket, user_name, group_name):
    """
    Joins new client to an existing or a new group.
    :param socket: Socket object
    :param user_name: String representing the user name
    :param group_name: String representing the group name
    :return: None.
    """
    join_msg = bytes('join;' + user_name + ';' + group_name + '\n', 'ascii')
    socket.sendall(join_msg)


# todo test this function
def add_shape(socket, shape_type, coordinates, color):
    """
    Sends the server the details of a new shape that drawn by the client
    :param socket: Socket object
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
    socket.sendall(shape_msg)


# todo test this function
def leave_client(socket):
    """
    Informs server that client has ended the session
    :param socket: Socket type object
    :return: None.
    """
    leave_msg = bytes('leave\n', 'ascii')
    socket.sendall(leave_msg)


# todo check this function
def handle_server_msgs(msg_type, msg_list):
    # todo documentation
    if msg_type == "join":
        print("join")
        joined_user_name = msg_list[1]
        DrawApp.join_user(joined_user_name)
        # someone joined the same group as this client
    elif msg_type == "shape":
        print("shape")
        shape_user_name = msg_list[1]
        shape_type = msg_list[2]
        shape_coordinates = msg_list[3]
        shape_color = msg_list[4]
        shape_tuple = (shape_user_name, shape_type, shape_coordinates,
                       shape_color)
        # todo call a function that draws the shape
        DrawApp.draw_shape(shape_tuple)
    elif msg_type == "leave":
        print("leave")
        quit_user_name = msg_list[1]
        #todo call function that updates users list
        DrawApp.leave_user(quit_user_name)
    elif msg_type == "users":
        print("users")
        current_group_users = msg_list[1].split(',')
        # todo call function that updates users list
        DrawApp.curr_group_users(current_group_users)

    elif msg_type == "error":
        error_msg = msg_list[1]
        print("error")

    # i  connected user names
    # ii shapes on panel
    # 2  join messages of new users
    # 3  new shapes mgs
    # 4  disconnection of other users
    # 5  error msg ??

    pass


def interact_with_server(server_address, server_port, user_name, group_name):
    client_socket = socket.socket()
    # connect to server
    client_socket.connect((server_address, server_port))
    join_user(client_socket, user_name, group_name)

    tny = True
    while tny:
        r, w, x = select.select([client_socket], [], [], 5)
        for sock in r:
            if sock == client_socket:
                data = r[0].recv(BUFFER_SIZE)
                msg_list = data.decode('ascii').strip().split(';')
                handle_server_msgs(msg_list[0], msg_list)
                print("data:"+str(msg_list))

    print('hello')
    client_socket.close()



if __name__ == '__main__':
    # if len(sys.argv) != PARAMETERS_NUM:
    #     print(ERROR_WRONG_PARAMETER_NUM)
    # elif legal_input(sys.argv[USER_NAME], sys.argv[GROUP_NAME]):
    #     server_address = sys.argv[SERVER_ADDRESS]
    #     server_port = sys.argv[SERVER_PORT]
    #     user_name = sys.argv[USER_NAME]
    #     group_name = sys.argv[GROUP_NAME]
    # server_address = 'localhost'
    # server_port = '5678'
    # user_name = 'Genos'
    # group_name = 's_class'
    server_address = input("enter_address ")
    server_port = input("enter port ")
    user_name = input("enter user name ")
    group_name = input("enter group name ")
    if legal_input(user_name, group_name):
        gui_environment = DrawApp(user_name)
        gui_environment.root.mainloop()
        # interact_with_server(server_address, int(server_port), user_name,
        #                      group_name)

    # tests
    # print('server add ', server_address,
    #       '\nserver port', server_port,
    #       '\nuser name', user_name,
    #       '\ngroup_name', group_name)
