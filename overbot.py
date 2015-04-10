# -*- coding: utf-8 -*-

if __name__ != '__main__':
    raise ImportError('This file is not intended for importing')

import irc
import shlex
import time
import json
import re
import socket

#import zandronum
import dexparse

IgnoredStatic = ['LinkBot']

class OverBot(irc.IrcConnection):
    def __init__(self):
        irc.IrcConnection.__init__(self, 'irc.zandronum.com')
        self.names = ['Overbot', 'Overbot_', 'Overbot__']
        self.channels = ['#te-talk:waffles']
        self.load_channels()
        self.state = 'INIT'
        self.name = -1
        self.ready = False
        self.origin = ''
        self.usercache = {} #nickname -> [username, update_date]
        self.commands = [] #nickname, username, date, argv
        self.ref = dexparse.DEXParser('dex')
        time.sleep(10.0)
        self.ref.refresh()
        self.ref_last = time.time()
        self.ignore_list = {}
        
    def dump_channels(self):
        try:
            with open('channels.json', 'w') as f:
                f.write(json.dumps(self.channels))
        except:
            pass

    def load_channels(self):
        try:
            with open('channels.json', 'r') as f:
                self.channels = json.loads(f.read())
        except:
            pass
        
    def request_username(self, nickname):
        self.send_command('', 'PRIVMSG', ['NickServ'], 'acc %s *' % (nickname))
        
    def check_username(self, nickname):
        nickname = nickname.lower()
        if nickname not in self.usercache:
            return None
        nn = self.usercache[nickname]
        if time.time()-nn[1] > 10.0:
            return None
        return nn[0]
        
    def simple_origin(self, origin):
        oix = origin.find('!')
        if oix < 0:
            return origin
        return origin[:oix]

    def recv_command(self, origin, command, args, textarg):
        #print(repr({'origin': origin, 'command': command, 'args': args, 'textarg': textarg}))
        if self.state == 'INIT':
            self.try_name()
        elif command == 433 and self.state == 'NICK':
            self.try_name()
        elif command == 1: # welcome
            self.origin = self.names[self.name]
            self.state = 'ACTIVE'
            self.ready = True
            print('Connected to the server as %s' % (self.names[self.name]))
            # join channels now
            for channel in self.channels:
                lnex = channel.find(':')
                pwd = ''
                if lnex >= 0:
                    pwd = channel[lnex+1:]
                    channel = channel[:lnex]
                self.join_channel(channel, pwd)
        elif command == 'JOIN': # join message
            if self.simple_origin(origin) == self.origin:
                print('Joined channel %s.' % (textarg))
        elif command == 'PING':
            self.send_command('', 'PONG', args, textarg)
        elif command == 'PRIVMSG' or command == 'NOTICE':
            # from, to, message
            self.handle_chat(origin, args[0], textarg, command == 'NOTICE')
        
    def try_name(self):
        self.state = 'INIT'
        self.name += 1
        if self.name >= len(self.names):
            raise Exception('No names available')
        # execute a NICK command first
        self.state = 'NICK'
        self.send_command('', 'NICK', [self.names[self.name]], '')
        self.send_command('', 'USER', [self.names[self.name], '0', '*'], 'Server LinkBot: https://github.com/jewalky/overbot')
        
    def join_channel(self, ch, password=''):
        print('Joining channel %s%s...' % (ch, ' (using password)' if password else ''))
        self.send_command('', 'JOIN', [ch] if not password else [ch, password], '')
        
    def part_channel(self, ch):
        print('Leaving channel %s...' % (ch))
        self.send_command('', 'PART', [ch], '')
        
    def check_flood(self, nickname):
        nickname = nickname.lower()
        if nickname not in self.ignore_list:
            self.ignore_list[nickname] = [[time.time()], None] # list of last messages, "ignored until"
            return False
        else:
            ar = self.ignore_list[nickname]
            ar[0][0:0] = [time.time()]
            ar[0] = ar[0][0:5]
            if len(ar[0]) >= 5 and time.time()-ar[0][4] < 15.0:
                ar[1] = time.time()+30.0
                return True
            return False
            
    def is_ignored(self, nickname):
        nickname = nickname.lower()
        if nickname in self.ignore_list and time.time() < self.ignore_list[nickname][1]:
            return True
        return False
        
    def handle_chat(self, frm, to, msg, notice):
        global IgnoredStatic
        nickname = self.simple_origin(frm)
        if nickname in IgnoredStatic:
            return
        # handle normal chat
        if self.simple_origin(frm) == 'NickServ':
            if ' -> ' in msg and 'ACC' in msg: # acc reply
                msg = msg.split(' ')
                # msg[0] = who
                # msg[1] = ->
                # msg[2] = username
                # msg[3] = acc
                # msg[4] = level
                if msg[4] == '3':
                    self.usercache[msg[0].lower()] = [msg[2], time.time()]
                else:
                    self.usercache[msg[0].lower()] = ['', time.time()]
                return
        elif self.simple_origin(to) != self.origin:
            # zds://.../st links (and /za)
            try:
                found = False
                tmsg = msg
                #m = re.search(r'(zds\:\/\/([\d\.]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,})\/(st|za))', tmsg)
                m = re.search(r'(zds\:\/\/([\d\.]+|[a-zA-Z0-9][a-zA-Z0-9\-\.]+)\:\d+(?:\/(od|st|za))?)', tmsg)
                if m is not None and not self.is_ignored(nickname):
                    if self.check_flood(nickname):
                        self.send_command('', 'PRIVMSG', [to], '%s, you will be ignored for 30 seconds.' % (nickname))
                        return
                    link_grp = m.group(1).split('/')
                    #print(repr(link_grp))
                    link_addr = link_grp[2]
                    try:
                        link_proto = link_grp[3]
                    except:
                        link_proto = 'zd'
                    if link_proto == 'st':
                        link_proto = 'za'
                    if not link_proto:
                        link_proto = 'zd'
                    #print link_addr
                    #print link_proto
                    lex = link_addr.find(':')
                    link_addr_host = link_addr[:lex]
                    link_addr_port = link_addr[lex+1:]
                    try:
                        link_addr_host = socket.gethostbyname(link_addr_host)
                    except:
                        pass
                    link_addr = link_addr_host+':'+link_addr_port
                    servers = self.ref.servers
                    #with open('servers.json', 'w') as f:
                    #    f.write(json.dumps(servers, indent=4))
                    for srv in servers:
                        srv_addr = srv['ip']
                        if srv_addr == link_addr and srv['port'] == link_proto:
                            if 'name' in srv:
                                pl_play = srv['playing']
                                pl_spec = srv['clients']-pl_play
                                pl_bots = 0
                                playstr = []
                                if pl_play > 0:
                                    playstr.append('%d player%s' % (pl_play, 's' if pl_play>1 else ''))
                                if pl_spec > 0:
                                    playstr.append('%d spectator%s' % (pl_spec, 's' if pl_spec>1 else ''))
                                if pl_bots > 0:
                                    playstr.append('%d bot%s' % (pl_bots, 's' if pl_bots>1 else ''))
                                playstr = ('; '+unicode(', '.join(playstr)) if len(playstr) > 0 else '')
                                def escape(s):
                                    #s = s.replace('://', u':/\u200B/')
                                    #s = re.sub(r'(?i)www', u'ww\u200Bw', s)
                                    return s
                                self.send_command('', 'PRIVMSG', [to], u'\u200B%s (%s, Location: %s, Gametype: %s%s)' % (escape(srv['name']), srv_addr, srv['country'], srv['gametype'], playstr))
            except:
                raise
        # handle commands
        if msg[0] != '@' and ((self.simple_origin(to) != self.origin) or notice):
            return
        if msg[0] == '@':
            msg = msg[1:]
        argv = shlex.split(msg)
        username = self.check_username(self.simple_origin(frm))
        if username is None:
            self.request_username(self.simple_origin(frm))
        self.commands.append([frm, to, username, time.time(), argv])
        
    def execute_command(self, nickname, reply_to, username, date, args):
        if len(args) <= 0:
            return True # invalid command
        if time.time()-date > 10.0:
            return True # ignore command if it hanged up
        if username is None:
            username = self.check_username(self.simple_origin(nickname))
        if username is None:
            return False
        # ok now we have a hostname for the command author, his username, the date the command ran on, and the command itself in argv
        if self.simple_origin(reply_to) == self.origin:
            reply_to = self.simple_origin(nickname)
        cmd = args[0].lower()
        if cmd == 'hi':
            self.send_command('', 'PRIVMSG', [reply_to], 'Hello %s%s!' % (self.simple_origin(nickname), ' (username '+username+')' if username else ''))
        elif username != 'AlienOverlord':
            return True
            
        if cmd == 'join' and len(args) >= 2:
            chan = args[1].lower()
            cho = chan
            lnex = chan.find(':')
            pwd = ''
            if lnex >= 0:
                pwd = chan[lnex+1:]
                chan = chan[:lnex]
            if chan not in self.channels:
                self.channels.append(cho)
                self.dump_channels()
                self.join_channel(chan, pwd)
        elif cmd == 'part' and len(args) >= 2:
            chan = args[1]
            def checkchan(ch, chan):
                zz = ch.find(':')
                if zz >= 0:
                    ch = ch[:zz]
                if ch.lower() == chan.lower():
                    return False
                return True
            self.channels = [ch for ch in self.channels if checkchan(ch, chan)]
            self.dump_channels()
            self.part_channel(chan)
        return True
        
    def tick(self):
        self.commands = [cmd for cmd in self.commands if not self.execute_command(*cmd)]
        if time.time()-self.ref_last > 60:
            try:
                self.ref.refresh()
                self.ref_last = time.time()
            except:
                pass

cl = OverBot()
cl.run()
