#!/usr/bin/env python3

"""
Checker (healthcheck) for service marstalk
"""

import sys
import math
import socket
import errno


# the flag putting/checking into the service is successful
def service_up():
    """ Service UP status """
    print("[service is worked] - 101")
    sys.exit(101)


# service is available (available tcp connection)
# but it's impossible to put/get the flag
def service_corrupt():
    """ Service CORRUPT status """
    print("[service is corrupt] - 102")
    sys.exit(102)


# service is not available (maybe blocked port or service is down)
def service_down():
    """ Service DOWN status """
    print("[service is down] - 104")
    sys.exit(104)


if len(sys.argv) != 5:
    app = sys.argv[0]
    FLAG_EXAMPLE = "\"c01d4567-e89b-12d3-a456-426600000010\""
    print("""
Usage:
  """ + app + """ <host> (put|check) <flag_id> <flag>
Example:
  """ + app + """ "127.0.0.1" "put" "abcdifghr" """ + FLAG_EXAMPLE + """
""")
    print("\n\t" + sys.argv[0] + " ")
    print("\n")
    sys.exit(0)


class MarsTalk:
    """ class encode / decode """

    @staticmethod
    def encode(msg):
        """ encode """
        result = ''
        curr_value_registry = 0
        for simbol in msg:
            simbol_code = ord(simbol)
            if simbol_code == curr_value_registry:
                result = result + ">.<"
                continue
            _operator = ''
            if curr_value_registry > simbol_code:
                simbol_code = curr_value_registry - simbol_code
                _operator = '-'
            if curr_value_registry < simbol_code:
                simbol_code = simbol_code - curr_value_registry
                _operator = '+'
            result = result + ''
            squard_val = int(math.floor(math.sqrt(simbol_code)))
            curr1 = 0
            while curr1 < squard_val:
                curr1 = curr1 + 1
                result = result + "+"
            width = int(simbol_code / squard_val)
            result = result + '[>'
            i = 0
            while i < width:
                result = result + _operator
                i += 1
            if _operator == '-':
                curr_value_registry = curr_value_registry - width * squard_val
            if _operator == '+':
                curr_value_registry = curr_value_registry + width * squard_val
            result = result + '<-]>'
            width2 = simbol_code - width * squard_val
            while width2 > 0:
                width2 = width2 - 1
                if _operator == '-':
                    result = result + '-'
                    curr_value_registry = curr_value_registry - 1
                if _operator == '+':
                    result = result + '+'
                    curr_value_registry = curr_value_registry + 1
            result = result + '.<'
        return result

    @staticmethod
    def block(code):
        """ block """
        opened = []
        blocks = {}
        i = 0
        while i < len(code):
            if code[i] == '[':
                opened.append(i)
            elif code[i] == ']':
                blocks[i] = opened[-1]
                blocks[opened.pop()] = i
            i += 1
        return blocks

    @staticmethod
    def decode(msg):
        """ decode """
        msg = msg.strip()
        msg = ''.join(c for c in msg if c in '><+-.,[]')
        pos_x = i = 0
        registries = {0: 0}
        blocks = MarsTalk.block(msg)
        length = len(msg)
        result = ""
        while i < length:
            sym = msg[i]
            if sym == '>':
                pos_x += 1
                registries.setdefault(pos_x, 0)
            elif sym == '<':
                pos_x -= 1
            elif sym == '+':
                registries[pos_x] += 1
            elif sym == '-':
                registries[pos_x] -= 1
            elif sym == '.':
                result = result + chr(registries[pos_x])
            # elif sym == ',':
            #     registries[pos_x] = int(input('Input: '))
            elif sym == '[':
                if not registries[pos_x]:
                    i = blocks[i]
            elif sym == ']':
                if registries[pos_x]:
                    i = blocks[i]
            i += 1
        return result


HOST = sys.argv[1]
PORT = 4444
COMMAND = sys.argv[2]

f_id = sys.argv[3]
flag = sys.argv[4]


def send_msg(_sock, _msg):
    """ Send message """
    print("send_msg [" + _msg + "]")
    _msg = MarsTalk.encode(_msg)
    _msg += "\n"
    print("send_msg (enc) [" + _msg + "]")
    print("send_msg (dec) [" + MarsTalk.decode(_msg) + "]")
    _sock.send(_msg.encode())


def recv_msg(_sock):
    """ Recive message """
    msg = _sock.recv(1024).decode("utf-8")
    print("msg = [" + msg + "]")
    msg = MarsTalk.decode(msg)
    print("recv_msg: [" + msg + "]")
    return msg


def put_flag():
    """ Put Flag to Service """
    print("put_flag")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        recv_msg(sock)
        send_msg(sock, "put")
        recv_msg(sock)
        send_msg(sock, f_id)
        recv_msg(sock)
        send_msg(sock, flag)
        recv_msg(sock)
        sock.close()
    except socket.timeout:
        service_down()
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            service_down()
        else:
            print(serr)
            service_corrupt()
    except Exception as err:  # pylint: disable=broad-except
        print(err)
        service_corrupt()


def check_flag():
    """ Check flag on service """
    print("check_flag")
    flag2 = ""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        recv_msg(sock)
        send_msg(sock, "get")
        recv_msg(sock)
        print("f_id: " + f_id)
        send_msg(sock, f_id)
        flag2 = recv_msg(sock)
        print("flag2 = [" + flag2 + "]")
        sock.close()
    except socket.timeout:
        service_down()
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            service_down()
        else:
            print(serr)
            service_corrupt()
    except Exception as err:  # pylint: disable=broad-except
        print(err)
        service_corrupt()
    if flag != flag2:
        service_corrupt()


if COMMAND == "put":
    put_flag()
    check_flag()
    service_up()

if COMMAND == "check":
    check_flag()
    service_up()
