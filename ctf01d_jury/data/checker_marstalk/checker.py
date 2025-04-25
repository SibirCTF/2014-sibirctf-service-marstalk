#!/usr/bin/env python3

import sys
import math
import socket
import errno

# the flag putting/checking into the service is successful
def service_up():
    print("[service is worked] - 101")
    exit(101)

# service is available (available tcp connection) but it's impossible to put/get the flag
def service_corrupt():
    print("[service is corrupt] - 102")
    exit(102)

# service is not available (maybe blocked port or service is down)
def service_down():
    print("[service is down] - 104")
    exit(104)

if len(sys.argv) != 5:
    print("\nUsage:\n\t" + sys.argv[0] + " <host> (put|check) <flag_id> <flag>\n")
    print("Example:\n\t" + sys.argv[0] + " \"127.0.0.1\" put \"abcdifghr\" \"c01d4567-e89b-12d3-a456-426600000010\" \n")
    print("\n")
    exit(0)

# code = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
# res = run(code)
# print(res)

# list ++++++++++[>++++++++++<-]>++++++++.<+[>---<-]>.<+++[>+++<-]>+.<+[>+<-]>.<
# test2 ++++++++++[>+++++++++++<-]>++++++.<+++[>-----<-]>.<+++[>++++<-]>++.<+[>+<-]>.<++++++++[>--------<-]>--.<
# put ++++++++++[>+++++++++++<-]>++.<++[>++<-]>+.<+[>-<-]>.<
# get ++++++++++[>++++++++++<-]>+++.<+[>--<-]>.<+++[>+++++<-]>.<

# code2 = compile_str("get")
# print(code2)
# res2 = run(code2)
# print(res2)


class MarsTalk:

    """ class encode / decode """

    @staticmethod
    def encode(msg):
        """ encode """
        result = ''
        val2 = 0
        for c in msg:
            ch = ord(c)
            if ch == val2:
                result = result + ">.<"
                continue
            minus = ''
            if val2 > ch:
                ch = val2 - ch
                minus = '-'
            if val2 < ch:
                ch = ch - val2
                minus = '+'
            result = result + ''
            sq = int(math.floor(math.sqrt(ch)))
            curr1 = 0
            while curr1 < sq:
                curr1 = curr1 + 1
                result = result + "+"
            w = int(ch / sq)
            result = result + '[>'
            i1 = 0
            while i1 < w:
                result = result + minus
                i1 = i1 + 1

            if minus == '-':
                val2 = val2 - w * sq
            if minus == '+':
                val2 = val2 + w * sq
            result = result + '<-]>'
            w2 = ch - w * sq
            while w2 > 0:
                w2 = w2 - 1
                if minus == '-':
                    result = result + '-'
                    val2 = val2 - 1
                if minus == '+':
                    result = result + '+'
                    val2 = val2 + 1
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
    def parse(code):
        """ parse """
        return ''.join(c for c in code if c in '><+-.,[]')

    @staticmethod
    def decode(msg):
        """ decode """
        msg = msg.strip()
        msg = MarsTalk.parse(msg)
        x = i = 0
        bf = {0: 0}
        blocks = MarsTalk.block(msg)
        length = len(msg)
        result = ""
        while i < length:
            sym = msg[i]
            if sym == '>':
                x += 1
                bf.setdefault(x, 0)
            elif sym == '<':
                x -= 1
            elif sym == '+':
                bf[x] += 1
            elif sym == '-':
                bf[x] -= 1
            elif sym == '.':
                result = result + chr(bf[x])
            # elif sym == ',':
            #     bf[x] = int(input('Input: '))
            elif sym == '[':
                if not bf[x]:
                    i = blocks[i]
            elif sym == ']':
                if bf[x]:
                    i = blocks[i]
            i += 1
        return result

HOST = sys.argv[1]
PORT = 4444

COMMAND = sys.argv[2]

f_id = sys.argv[3]
flag = sys.argv[4]

def send_msg(_sock, _msg):
    print("send_msg [" + _msg + "]")
    _msg = MarsTalk.encode(_msg)
    _msg += "\n"
    print("send_msg (enc) [" + _msg + "]")
    print("send_msg (dec) [" + MarsTalk.decode(_msg) + "]")
    _sock.send(_msg.encode())

def recv_msg(_sock):
    msg = _sock.recv(1024).decode("utf-8")
    print("msg = [" + msg + "]")
    msg = MarsTalk.decode(msg)
    print("recv_msg: [" + msg + "]")
    return msg

# 1q2z2j9x8~
# 1q2w3e4r5t

def put_flag():
    print("put_flag")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        recv_msg(s)
        send_msg(s, "put")
        recv_msg(s)
        send_msg(s, f_id)
        recv_msg(s)
        send_msg(s, flag)
        recv_msg(s)
        s.close()
    except socket.timeout:
        service_down()
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            service_down()
        else:
            print(serr)
            service_corrupt()
    except Exception as e:
        print(e)
        service_corrupt()

def check_flag():
    print("check_flag")
    flag2 = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        recv_msg(s)
        send_msg(s, "get")
        recv_msg(s)
        print("f_id: " + f_id)
        send_msg(s, f_id)
        flag2 = recv_msg(s)
        print("flag2 = [" + flag2 + "]")
        s.close()
    except socket.timeout:
        service_down()
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            service_down()
        else:
            print(serr)
            service_corrupt()
    except Exception as e:
        print(e)
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
