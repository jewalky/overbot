# -*- coding: utf-8 -*-

import socket
import select
import time

class IrcConnection:
    def __init__(self, server):
        if ':' in server:
            sz = server.find(':')
            self.server = server[sz:]
            self.port = int(server[:sz+1])
        else:
            self.server = server
            self.port = 6667
        self.socket = None
        self.buffer = ''
        self.init()
       
    def init(self):
        pass

    def connect(self):
        if self.socket is not None:
            self.disconnect()
        self.socket = socket.socket()
        self.socket.connect((self.server, self.port))
        self.socket.setblocking(0)
        self.buffer = ''
        self.init()

    def disconnect(self):
        if self.socket is None:
            return
        self.socket.close()
        
    def tick(self):
        pass

    def run(self):
        if self.socket is None:
            self.connect()
        try:
            while True:
                self.tick()
                try:
                    self.buffer += self.socket.recv(1024)
                except socket.error as e:
                    if e.errno == 10035: #windows
                        time.sleep(0.001)
                        continue
                    self.disconnect()
                    raise
                while True:
                    n = self.buffer.find('\r\n')
                    if n <= 0:
                        break
                    line = self.buffer[:n]
                    self.buffer = self.buffer[n+2:]
                    try:
                        self.recv_line(line.decode('utf-8'))
                    except Exception as e:
                        print('Caught exception %s while processing the line' % (repr(e)))
        except KeyboardInterrupt:
            pass
        self.disconnect()
        
    def recv_line(self, line):
        cmd_origin = ''
        cmd_command = ''
        cmd_numeric = -1
        cmd_args = []
        cmd_textarg = ''
        
        if line[0] == ':':
            lnex = line.find(' ')
            if lnex < 0:
                self.invalid_line(line)
                return
            cmd_origin = line[1:lnex]
            line = line[lnex+1:]

        lnex = line.find(' :')
        if lnex >= 0:
            cmd_textarg = line[lnex+2:]
            line = line[:lnex]
            
        lnex = line.find(' ')
        if lnex < 0:
            lnex = len(line)
        cmd_command = line[:lnex]
        try:
            cmd_numeric = int(cmd_command)
        except:
            pass
        line = line[lnex+1:]
        if line:
            cmd_args = line.split(' ')
        
        self.recv_command(cmd_origin, cmd_numeric if cmd_numeric >= 0 else cmd_command, cmd_args, cmd_textarg)
                
    def invalid_line(self, line):
        print('Warning: odd line received from the server:\n%s' % (line))

    def recv_command(self, origin, command, args, textarg):
        print(repr({'origin': origin, 'command': command, 'args': args, 'textarg': textarg}))
        
    def send_command(self, origin, command, args, textarg):
        s = ''
        if origin != '':
            s += ':'+origin+' '
        s += str(command)
        if len(args):
            s += ' '+' '.join(args)
        if textarg:
            s += ' :'+textarg
        s += '\r\n'
        self.send_line(s)
        
    def send_line(self, line):
        if self.socket is None:
            raise Exception('Connection is offline!')
        self.socket.send(line.encode('utf-8'))
