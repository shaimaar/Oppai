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

MSG_TYPE = 0
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

        self.help_button = tki.Button(text="Help").grid(row=0, column=0)
        self.color_label = Label(self.root, text="Choose a color")
        self.color_label.grid(row=1, column=0)

        self.shape_label = Label(self.root, text="Choose a shape")
        self.shape_label.grid(row=2, column=0)

        self.users_list_box = tki.Listbox()
        self.users_list_box.grid(row=3, column=0)

        self.create_canvas()
        self.build_color_buttons()
        self.build_shape_buttons()

        # self.root.after(10,self)
        root = Tk()  # call the constructor of class to create blank window
        # put it in infinite loop, so the window will continuously be displayed till
        # will will press the exit button
        # todo call interact_with_server

        self.join_user_to_server()
        self.interact_with_server()
        root.mainloop()


    def create_canvas(self):
        self.canvas = tki.Canvas(self.root, width=CANVAS_WIDTH,\
                                 height=CANVAS_HEIGHT, bg=CANVAS_BACKGROUND)
        self.canvas.grid(row=3, column=1)
        self.canvas.bind("<Button-1>", self.click)

    def build_color_buttons(self):
        index = 2
        for color in self.colors_list:
            curr_color_button = tki.Button(text=color, command=self.
                                           color_buttons_command(color))
            curr_color_button.grid(row=1, column=index)
            self.buttons_list.append(curr_color_button)
            index += 1

    def build_shape_buttons(self):
        index = 2
        for shape in self.shapes_list:
            curr_shape_button = tki.Button(text=shape, command=self.
                                           shape_buttons_command(shape))
            curr_shape_button.grid(row=2, column=index)
            self.buttons_list.append(curr_shape_button)
            index += 1

    def shape_buttons_command(self, shape):
        def change_cur_shape():
            self.clicks = []
            self.cur_shape = shape
        return change_cur_shape

    def color_buttons_command(self, color):
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
                                       width=3, outline="black")

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
            if name != self.user_name:
                self.users_of_group.append(name)
        self.update_users_list_box()

    def update_users_list_box(self):
        """
        update users_list_box by users of users_of_group list
        :return:
        """
        for user in self.users_of_group:
            self.users_list_box.insert(0, user)

    def interact_with_server(self):
        """

        :param server_port:
        :param user_name:
        :param group_name:
        :return:
        """

        # tny = True
        # while tny:
        r, w, x = select.select([self.client_socket], [], [], 0.01)
        for sock in r:
            if sock == self.client_socket:
                data = r[0].recv(BUFFER_SIZE)
                # msg_list = data.decode('ascii').strip().split(';')
                msg_list = data.decode('ascii').split('\n')
                for msg in msg_list:
                    parse_msg_list = msg.split(';')
                    self.handle_server_msgs(parse_msg_list[MSG_TYPE], parse_msg_list)
                    print("data:"+str(msg))
        self.root.after(3000, self.interact_with_server)


    def join_user_to_server(self):
        """
        Joins new client to an existing or a new group.
        :return: None.
        """
        join_msg = bytes('join;' + user_name + ';' + group_name + '\n', 'ascii')
        self.client_socket.sendall(join_msg)


    # todo test this function
    def add_shape(self, shape_type, coordinates, color):
        """
        Sends the server the details of a new shape that drawn by the client
        :param shape_type: String representing the name of the shape: rectangle |
        | triangle | oval | line.
        :param coordinates: A list representing a list of coordinates
        :param color:
        :return: None
        """
        print("call uuuuuuuuu")
        print(shape_type)
        print(coordinates)
        # convert list of int coordinated to string
        coordinates_str = ','.join(str(coord) for coord in coordinates)
        shape_msg = bytes('shape;' + shape_type + ';' + coordinates_str +
                          ';' + color + '\n', 'ascii')
        self.client_socket.sendall(shape_msg)


    # todo test this function
    def leave_client(self):
        """
        Informs server that client has ended the session
        :return: None.
        """
        leave_msg = bytes('leave\n', 'ascii')
        self.client_socket.sendall(leave_msg)


    # todo check this function
    def handle_server_msgs(self, msg_type, msg_list):
        # todo documentation
        if msg_type == "join":
            print("join")
            joined_user_name = msg_list[1]
            self.join_user(joined_user_name)
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
            self.draw_shape(shape_tuple)
        elif msg_type == "leave":
            print("leave")
            quit_user_name = msg_list[1]
            #todo call function that updates users list
            DrawApp.leave_user(quit_user_name)
        elif msg_type == "users":
            print("users")
            current_group_users = msg_list[1].split(',')
            # todo call function that updates users list
            self.curr_group_users(current_group_users)

        elif msg_type == "error":
            error_msg = msg_list[1]
            print("error")




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
        client_socket = socket.socket()
        # connect to server
        client_socket.connect((server_address, int(server_port)))


        gui_environment = DrawApp(user_name, group_name, client_socket)
        # gui_environment.root.after(1000, interact_with_server(server_address,
        #                             int(server_port), user_name, group_name))
        gui_environment.root.mainloop()
        # interact_with_server(server_address, int(server_port), user_name,
        #                      group_name)

    # tests
    # print('server add ', server_address,
    #       '\nserver port', server_port,
    #       '\nuser name', user_name,
    #       '\ngroup_name', group_name)
# todo self.client_socket.close()