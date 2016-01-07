#!/usr/bin/env python3

import socket
import sys
import traceback

MSGDELIM = b'\n'
DELIM = b';'
FIELDSEP = b','
MAX_MSG_SIZE = 1048


def exchange(sock, msg):
    sock.sendall(msg+MSGDELIM)
    buf = b' '
    data = b''
    while buf[-len(MSGDELIM):]!=MSGDELIM:
        buf = sock.recv(MAX_MSG_SIZE)
        data += buf
    return data[:-1].split(DELIM)


def getgroupnames(sock):
    groups = exchange(sock,b'groups')[1].split(FIELDSEP)
    return [g for g in groups if g]


def getgroupmembers(sock,gnames):
    gmembers = {}
    for name in gnames:
        data = exchange(sock,DELIM.join((b'who',name)))
        if data[0] == b'users':
            gmembers[name.decode()] = data[1].decode().split(FIELDSEP.decode())
    return gmembers    


def main():
    if len(sys.argv) < 3:
        print('Usage : python online_info_client.py hostname port')
        return
    host = sys.argv[1]
    port = int(sys.argv[2])
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        # asking for all connected groups
        gnames = getgroupnames(sock)
        # get members in each group
        gmembers = getgroupmembers(sock,gnames)
        print(gmembers)
    except:
        traceback.print_exc()
    finally:
        sock.close()

if __name__ == '__main__':
    main()
