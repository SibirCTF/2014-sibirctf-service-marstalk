#!/usr/bin/env python3

"""
MarsTalk - Service with Vulnerabilities
"""

import socket
import threading
import math
import re
import os

HOST = ""
PORT = 4444
DEBUG_MODE = False
thrs = []


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
    def decode(msg):
        """ decode """
        msg = msg.strip()
        msg = ''.join(c for c in msg if c in '><+-.,[]')
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


class MarsTalkConnect(threading.Thread):
    """ Connect Client """

    def __init__(self, _sock, _addr):
        self.__sock = _sock
        # self.__addr = _addr
        self.b_kill = False
        threading.Thread.__init__(self)

    def __send(self, msg):
        """ send message """
        # debug
        if not DEBUG_MODE:
            msg = MarsTalk.encode(msg)
        msg = "\n" + msg + "\n\n"
        self.__sock.send(msg.encode())

    def __read(self):
        buf = self.__sock.recv(1024)
        buf = buf.decode("utf-8")
        if not DEBUG_MODE:
            buf = MarsTalk.decode(buf)
        return buf

    def __command_put(self):
        self.__send("id = ")
        f_id = self.__read()
        if f_id == "":
            return
        f_id = re.search(r'\w*', f_id).group()
        if f_id == "":
            self.__send("incorrect id")
            return
        self.__send("flag = ")
        f_text = self.__read()
        if f_text == "":
            return
        with open('flags/'+f_id, 'w', encoding='utf-8') as _file:
            _file.write(f_text)
        return

    def __command_get(self):
        self.__send("id = ")
        f_id = self.__read()
        if f_id == "":
            return
        f_id = re.search(r'\w*', f_id).group()
        if f_id == "":
            self.__send("incorrect id")
            return
        if os.path.exists('flags/' + f_id):
            with open('flags/' + f_id, 'r', encoding='utf-8') as _file:
                line = _file.readline()
            self.__send(line)
        else:
            self.__send("id not found")

    def __command_list(self):
        for f in os.listdir('flags/'):
            self.__send("file: " + f)

    def __command_close(self):
        self.__send("Bye-bye\n")

    def run(self):
        help_s = "\nCommands: put, get, list, close\n>\n\n"
        # ptrn = re.compile(r""".*(?P<name>\w*?).*""", re.VERBOSE)
        self.__send(help_s)
        _commands = {
            "put": self.__command_put,
            "get": self.__command_get,
            "list": self.__command_list,
            "close": self.__command_close,
        }
        while True:
            if self.b_kill:
                break
            buf = self.__read()
            if buf == "":
                break
            command = re.search(r'\w*', buf).group()
            if command in _commands:
                _commands[command]()
                break
            if command:
                self.__send("[" + command + "] unknown command\n")
                break
        self.b_kill = True
        self.__sock.close()
        thrs.remove(self)

    def kill(self):
        """ stop and kill all """
        if self.b_kill is True:
            return
        self.b_kill = True
        self.__sock.close()
        # thrs.remove(self)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)

if not os.path.exists("flags"):
    os.makedirs("flags")

try:
    while True:
        sock, addr = s.accept()
        thr = MarsTalkConnect(sock, addr)
        thrs.append(thr)
        thr.start()
except KeyboardInterrupt:
    print('Bye! Write me letters!')
    s.close()
    for thr in thrs:
        thr.kill()
