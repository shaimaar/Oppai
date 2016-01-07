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

############################################################
# Constants
############################################################

SERVER_ADDRESS = 1
SERVER_PORT = 2
USER_NAME = 3
GROUP_NAME = 4
PARAMETERS_NUM = 5
ERROR_USER_NAME_MSG = 'Error. User name must be less than 20 characters'
ERROR_GROUP_NAME_MSG = 'Error. Group name must be less than 20 characters'
ERROR_BAD_CHARACTERS_MSG = 'Error. user name and group name must contain ' \
                           'numbers and English characters only'
ERROR_WRONG_PARAMETER_NUM = "Wrong number of parameters. The correct usage" \
                            "is:\npython client.py e-intro.cs.huji.ac.il " \
                            "8000,<user_name> <group_name>"
BUFFER_SIZE = 1024
MSG_DELIMITER = b'\n'

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
        # someone joined the same group as this client
    elif msg_type == "shape":
        print("shape")
        shape_user_name = msg_list[1]
        shape_line = msg_list[2]
        shape_coordinates = msg_list[3]
        shape_color = msg_list[4]
        # todo call a function that draws the shape
    elif msg_type == "leave":
        print("leave")
        quit_user_name = msg_list[1]
        #todo call function that updates users list
    elif msg_type == "users":
        print("users")
        current_group_users = msg_list[1].split(',')
        # todo call function that updates users list
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
        interact_with_server(server_address, int(server_port), user_name,
                             group_name)
    # tests
    # print('server add ', server_address,
    #       '\nserver port', server_port,
    #       '\nuser name', user_name,
    #       '\ngroup_name', group_name)
