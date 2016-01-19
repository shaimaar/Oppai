#############################################################
# FILE : ex12.py
# Writer #1: Shai Maarek , shaimaar , 305456261
# Writer #2: Oren Sultan, orens, 201557972
# DESCRIPTION: Implementation of Client Server and Gui App
# which allows the clients to draw shapes on screen.
# Output: GUI and Terminal
#############################################################

############################################################
# Imports
############################################################
import sys
import socket
import re
import select
import tkinter as tk

############################################################
# Constants
############################################################

# sys arg parameters
SERVER_ADDRESS = 1
SERVER_PORT = 2
USER_NAME = 3
GROUP_NAME = 4
PARAMETERS_NUM = 5

# input validation
MAX_CHAR_LEN = 20
NO_INPUT = 0

# time
TIME_LAPSE = 3000
TIMEOUT = 0.05

# list indexes
MSG_TYPE = 0
MSG_INDEX = 0
USER_NAME_LOC = 1
ERROR_MSG_LOC = 1
SHAPE_LOC = 2
SHAPE_COORD_LOC = 3
SHAPE_COLOR_LOC = 4

COORD_X_INDEX = 0
COORD_Y_INDEX = 1

HELP_MENU_WIDTH = 250
ERR_MSG_WIDTH = 600

LIST_BOX_WIDTH = 30
LIST_BOX_HEIGHT = 30

BUTTONS_START_INDEX = 2

# canvas design
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
CANVAS_BACKGROUND = "white"
CANVAS_BORDER_WIDTH = 10

SHAPE_COLOR_INDEX = 3
SHAPE_COORDS_INDEX = 2
SHAPE_TYPE_INDEX = 1
USER_NAME_INDEX = 0

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
MSG_DELIMITER = '\n'
ERROR_INPUT_20_MSG = 'Error. Input must be less than 20 characters.'
ERROR_INPUT_0_MSG = 'Error. Please enter a string.'
ENTER_NEW_USER_NAME_MSG = 'Please choose a new user name consisted of ' \
                              'numbers and letters and less then 20 letters: '
ENTER_NEW_GROUP_NAME_MSG = 'Please choose a new group name consisted of ' \
                              'numbers and letters and less then 20 letters: '
ERROR_WRONG_PARAMETER_NUM = "Wrong number of parameters. The correct usage" \
                            "is:" + MSG_DELIMITER + "python client.py " \
                            "e-intro.cs.huji.ac.il " \
                            "8000,<user_name> <group_name>"
BUFFER_SIZE = 1024


class DrawApp:
    """
    Class DrawApp is responsible of the management of the App
    """
    def __init__(self, user_name, group_name, client_socket):
        """
        constructor of DrawApp class
        :param user_name: String representing user name
        :param group_name: String representing group name
        :param client_socket: Socket object
        :return: None
        """
        self.root = tk.Tk()
        self.buttons_list = []
        self.clicks = []
        self.num_of_clicks = 0
        self.users_of_group = []

        self.cur_shape = DEFAULT_SHAPE
        self.cur_color = DEFAULT_COLOR

        self.colors_list = [RED, BLUE, YELLOW, GREEN, BLACK, VIOLET, ORANGE]
        self.shapes_list = [LINE, RECTANGLE, CIRCLE, TRIANGLE]

        # to present the name of the user_name on the window
        self._user_name = user_name
        self.root.title(user_name)

        self._group_name = group_name
        self._client_socket = client_socket

        self.color_label = tk.Label(self.root, text="Choose a color")
        self.color_label.grid(row=1, column=0)

        self.shape_label = tk.Label(self.root, text="Choose a shape")
        self.shape_label.grid(row=2, column=0)

        self.users_list_box = tk.Listbox(self.root, width=LIST_BOX_WIDTH,
                                         height=LIST_BOX_HEIGHT)
        self.users_list_box.grid(row=3, column=0)

        self.create_help_menu()
        self.create_canvas()
        self.create_color_buttons()
        self.create_shape_buttons()

        self.join_user_to_server()

        self.interact_with_server()

        # call on_closing when user close the window of App
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # put it in infinite loop, so the window will continuously
        # be displayed till will will press the exit button
        self.root.mainloop()

    def on_closing(self):
        """
        regulated exit from App
        :return: None
        """
        self.root.destroy()
        self.leave_client()
        self._client_socket.close()

    def create_help_menu(self):
        """
        Create help menu with instructions to the user
        :return: None
        """
        menu = tk.Menu(self.root)
        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Instructions", command=self.instructions)
        self.root.config(menu=menu)

    @staticmethod
    def instructions():
        """
        Present to the user help instructions of the Application
        :return: None
        """
        top = tk.Toplevel()
        top.title("instructions")
        msg = tk.Message(top, text="App Instructions: Hi, Please choose "
                                   "color and a shape by clicking the button "
                                   "then click on the canvas."
                                   "3 clicks for triangle, and 2 "
                                   "clicks for other shapes.",
                         width=HELP_MENU_WIDTH)
        msg.pack()

    @staticmethod
    def raise_error_msg(err_msg):
        """
        Present to the use the error message from server
        :param err_msg: String representing error message
        :return: None
        """
        top = tk.Toplevel()
        top.title("Error")
        msg = tk.Message(top, text=err_msg, width=ERR_MSG_WIDTH)
        msg.pack()

    def create_canvas(self):
        """
        Create the canvas with the defined width, height and border width
        Here the user will click to draw the shapes
        :return: None
        """
        self.canvas = \
            tk.Canvas(self.root, width=CANVAS_WIDTH,
                      height=CANVAS_HEIGHT,
                      borderwidth=CANVAS_BORDER_WIDTH,
                      bg=CANVAS_BACKGROUND, relief='raised')
        self.canvas.grid(row=3, column=1)
        self.canvas.bind("<Button-1>", self.click)

    def create_color_buttons(self):
        """
        Create a list of buttons for colors
        call command_color_buttons to change the cur_color accordingly
        :return: None
        """
        index = BUTTONS_START_INDEX
        for color in self.colors_list:
            curr_color_button = tk.Button(text=color,
                                          command=self.command_color_buttons
                                          (color)).\
                grid(row=1, column=index, sticky=tk.W)
            self.buttons_list.append(curr_color_button)
            index += 1

    def create_shape_buttons(self):
        """
        Create a list of buttons for shapes
        call command_shape_buttons to change the cur_shape accordingly
        :return: None
        """
        index = BUTTONS_START_INDEX
        for shape in self.shapes_list:
            curr_shape_button = tk.Button(text=shape,
                                          command=self.command_shape_buttons
                                          (shape))
            curr_shape_button.grid(row=2, column=index)
            self.buttons_list.append(curr_shape_button)
            index += 1

    def command_shape_buttons(self, shape):
        """
        :param shape: String representing shape name
        :return: the new selected shape
        """
        def change_cur_shape():
            # it's a new choice of shape, so initialize the clicks list
            self.clicks = []
            self.cur_shape = shape
        return change_cur_shape

    def command_color_buttons(self, color):
        """
        :param color: Sting representing color name
        :return: the new selected color
        """
        def change_cur_color():
            # it's a new choice of color, so initialize the clicks list
            self.clicks = []
            self.cur_color = color
        return change_cur_color

    def draw_shape(self, shape_tuple):
        """
        draw a shape in a specific color and position according to user
        :param shape_tuple: Tuple type object with shape's details
        :return: None
        """
        # extract the coordinates
        coords = shape_tuple[SHAPE_COORDS_INDEX].split(',')
        # if line
        if shape_tuple[SHAPE_TYPE_INDEX] == LINE:
            self.canvas.create_line(coords,
                                    fill=shape_tuple[SHAPE_COLOR_INDEX])
        # if rectangle
        elif shape_tuple[SHAPE_TYPE_INDEX] == RECTANGLE:
            self.canvas.create_rectangle(coords,
                                         fill=shape_tuple[SHAPE_COLOR_INDEX])
        # if circle
        elif shape_tuple[SHAPE_TYPE_INDEX] == CIRCLE:
            self.canvas.create_oval(coords,
                                    fill=shape_tuple[SHAPE_COLOR_INDEX])
        # if triangle
        else:
            self.canvas.create_polygon(coords,
                                       fill=shape_tuple[SHAPE_COLOR_INDEX])

        # draw text on the canvas shape
        self.canvas.create_text(coords[COORD_X_INDEX], coords[COORD_Y_INDEX],
                                text=shape_tuple[USER_NAME_INDEX])

    def click(self, event):
        """
        listener to click event, we will extract the coords and draw the
        suitable shape according to user request
        :param event: Event type object
        :return: None
        """
        # coordinates of user click
        self.clicks.append(event.x)
        self.clicks.append(event.y)

        self.num_of_clicks += 1
        # only in this case we will want to draw a shape
        if ((self.num_of_clicks == 2 and self.cur_shape != TRIANGLE) or
            (self.num_of_clicks == 3 and self.cur_shape == TRIANGLE)):
            # call add shape to informs the server
            self.add_shape(self.cur_shape, self.clicks, self.cur_color)
            # initialize clicks list and num of clicks
            self.clicks = []
            self.num_of_clicks = 0

    def join_user(self, user_name):
        """
        add user to users_of_group list
        call update_users_list_box, so we will see the update on screen
        :param user_name: String representing user name
        :return: None
        """
        self.users_of_group.append(user_name)
        self.update_users_list_box()

    def leave_user(self, user_name):
        """
        remove the user from users_of_group list if he left
        call update_users_list_box, so we will see the update on screen
        :param user_name: String representing user name
        :return: None
        """
        if user_name in self.users_of_group:
            self.users_of_group.remove(user_name)
        self.update_users_list_box()

    def curr_group_users(self, curr_group):
        """
        add all of the users to users of group list
        call update_users_list_box, so we will see the update on screen
        :param curr_group: Sting representing group name
        :return: None
        """
        # run all of the names of users in the group
        for name in curr_group:
            # add the other users to the group
            self.users_of_group.append(name)
        self.update_users_list_box()

    def update_users_list_box(self):
        """
        update users_list_box by users of users_of_group list
        :return: None
        """
        # first delete the users_list_box, then insert all of the users.
        # in order to avoid duplicates
        self.users_list_box.delete(0, tk.END)

        self.users_list_box.insert(tk.END, self._group_name)
        self.users_list_box.insert(tk.END, "users online:")

        # add all of users which are belong to this group
        for user in self.users_of_group:
            self.users_list_box.insert(tk.END, user)

    def interact_with_server(self):
        """
        Checks if a message was received using select, and transfers
        messages to
        functions
        that handle them.
        :return: None.
        """
        r, w, x = select.select([self._client_socket], [], [], TIMEOUT)
        for sock in r:
            if sock == self._client_socket:
                data = r[MSG_INDEX].recv(BUFFER_SIZE)
                msg_list = data.decode('ascii').split(MSG_DELIMITER)
                for msg in msg_list:
                    parse_msg_list = msg.split(';')
                    self.handle_server_msgs(parse_msg_list[MSG_TYPE],
                                            parse_msg_list)
        self.root.after(TIME_LAPSE, self.interact_with_server)

    def join_user_to_server(self):
        """
        Joins new client to an existing or a new group.
        :return: None.
        """
        join_msg = bytes('join;' + self._user_name + ';' + self._group_name +
                         MSG_DELIMITER, 'ascii')
        self._client_socket.sendall(join_msg)

    def add_shape(self, shape_type, coordinates, color):
        """
        Sends the server the details of a new shape that drawn by the client
        :param shape_type: String representing the name of the shape:
        rectangle |
        | triangle | oval | line.
        :param coordinates: A list representing a list of coordinates
        :param color:
        :return: None
        """
        # convert list of int coordinated to string
        coordinates_str = ','.join(str(coord) for coord in coordinates)
        shape_msg = bytes('shape;' + shape_type + ';' + coordinates_str +
                          ';' + color + MSG_DELIMITER, 'ascii')
        self._client_socket.sendall(shape_msg)

    def leave_client(self):
        """
        Informs server that client has ended the session
        :return: None.
        """
        leave_msg = bytes('leave'+MSG_DELIMITER, 'ascii')
        self._client_socket.sendall(leave_msg)

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

    def get_user_name(self):
        """
        Returns the user name of the client
        :return: String representing the user name of the client
        """
        return self._user_name

    def get_group_name(self):
        """
        Returns the group name of the client
        :return: String representing the group name of the client
        """
        return self._group_name

    def get_scoket(self):
        """
        Returns the socket of the client
        :return: Socket type object
        """
        return self._client_socket

def legal_input(name):
    """
    Receives a string and checks if it's 20 characters or less, and if it
    contains letters and numbers only.
    :param name: String.
    :return: Boolean value - False if a parameter isn't legal, else returns
    True
    """
    if len(name) >= MAX_CHAR_LEN:
        print(ERROR_INPUT_20_MSG)
        return False
    elif len(name) == NO_INPUT:
        print(ERROR_INPUT_0_MSG)
        return False
    # Checks is name contains letters and numbers only using regular expression
    # elif re.match("^[\w\d]*$", name):
    elif re.match("^[A-Za-z0-9]*$", name):
        return True
    else:
        return False


if __name__ == '__main__':
    if len(sys.argv) != PARAMETERS_NUM:
        print(ERROR_WRONG_PARAMETER_NUM)
    else:
        user_name = sys.argv[USER_NAME]
        group_name = sys.argv[GROUP_NAME]
        server_address = sys.argv[SERVER_ADDRESS]
        server_port = sys.argv[SERVER_PORT]
        while not legal_input(user_name):
            user_name = input(ENTER_NEW_USER_NAME_MSG)
        while not legal_input(group_name):
            group_name = input(ENTER_NEW_GROUP_NAME_MSG)
        # create socket and connect to server
        client_socket = socket.socket()
        client_socket.connect((server_address, int(server_port)))
        # create new GUI object and connect to server
        gui_environment = DrawApp(user_name, group_name, client_socket)
