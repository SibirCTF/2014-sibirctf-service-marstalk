#!/usr/bin/python2
import sys
import math 
import socket
import random

def block(code):
    opened = []
    blocks = {}
    for i in range(len(code)):
        if code[i] == '[':
            opened.append(i)
        elif code[i] == ']':
            blocks[i] = opened[-1]
            blocks[opened.pop()] = i
    return blocks
 
def parse(code):
    return ''.join(c for c in code if c in '><+-.,[]')
 
def run(code):
    code = parse(code)
    x = i = 0
    bf = {0: 0}
    blocks = block(code)
    l = len(code)
    result = ""
    while i < l:
        sym = code[i]
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
        elif sym == ',':
            bf[x] = int(input('Input: '))
        elif sym == '[':
            if not bf[x]: i = blocks[i]
        elif sym == ']':
            if bf[x]: i = blocks[i]
        i += 1
    return result

def compile_str(msg):
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
		w = ch / sq
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
     
host = sys.argv[1]
port = 4444

f_id = str(random.randrange(1,2000));
flag = sys.argv[3]

print "try connect " + host + ":4444";

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	result = s.recv(1024)
	# print run(result)
	s.send(compile_str("put") + "\n")
	result = s.recv(1024)
	s.send(compile_str(f_id) + "\n")
	result = s.recv(1024)
	s.send(compile_str(flag) + "\n")
	result = s.recv(1024)
	s.close()
except:
	print "[service is currupt]"
	sys.exit(-1)

flag2 = ""

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	result = s.recv(1024)
	# print run(result)
	s.send(compile_str("get") + "\n")
	result = s.recv(1024)
	s.send(compile_str(f_id) + "\n")
	result = s.recv(1024)
	flag2 = run(result)
	s.close()
except:
	print "[service is currupt]"
	sys.exit(-1)
	
if flag == flag2:
	print "[service is worked]"
else:
	print "[service is currupt]"
