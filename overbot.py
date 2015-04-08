# -*- coding: utf-8 -*-

if __name__ != '__main__':
    raise ImportError('This file is not intended for importing')

import irc
import shlex
import time
import json
import re
import socket

import zandronum

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
        self.ref = zandronum.ZandronumRefresher()
        self.ref.refresh()
        self.ref_last = time.time()
        
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
        self.send_command('', 'USER', [self.names[self.name], '0', '*'], 'Alien Overbot')
        
    def join_channel(self, ch, password=''):
        print('Joining channel %s%s...' % (ch, ' (using password)' if password else ''))
        self.send_command('', 'JOIN', [ch] if not password else [ch, password], '')
        
    def part_channel(self, ch):
        print('Leaving channel %s...' % (ch))
        self.send_command('', 'PART', [ch], '')
        
    def handle_chat(self, frm, to, msg, notice):
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
                m = re.search(r'(zds\:\/\/([\d\.]+|[a-zA-Z0-9][a-zA-Z0-9\-\.]+)\:\d+\/(st|za))', tmsg)
                if m is not None:
                    link_addr = m.group(1).split('/')[2]
                    lex = link_addr.find(':')
                    link_addr_host = link_addr[:lex]
                    link_addr_port = link_addr[lex+1:]
                    try:
                        link_addr_host = socket.gethostbyname(link_addr_host)
                    except:
                        pass
                    link_addr = link_addr_host+':'+link_addr_port
                    servers = self.ref.servers
                    if len(servers) == 0:
                        servers = self.ref.old_servers
                    for srv in servers:
                        srv_addr = '%s:%d' % (srv.addr[0], srv.addr[1])
                        if srv_addr == link_addr:
                            if not srv.na:
                                pl_play = 0
                                pl_spec = 0
                                pl_bots = 0
                                for player in srv.players:
                                    if player.spectator:
                                        pl_spec += 1
                                    elif player.bot:
                                        pl_bots += 1
                                    else:
                                        pl_play += 1
                                playstr = []
                                if pl_play > 0:
                                    playstr.append('%d player%s' % (pl_play, 's' if pl_play>1 else ''))
                                if pl_spec > 0:
                                    playstr.append('%d spectator%s' % (pl_spec, 's' if pl_spec>1 else ''))
                                if pl_bots > 0:
                                    playstr.append('%d bot%s' % (pl_bots, 's' if pl_bots>1 else ''))
                                playstr = ('; '+unicode(', '.join(playstr)) if len(playstr) > 0 else '')
                                self.send_command('', 'PRIVMSG', [to], '%s (%s, Gametype: %s%s)' % (srv.title, srv_addr, srv.game_mode_as_string(), playstr))
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
            self.ref.refresh()
            self.ref_last = time.time()

cl = OverBot()
cl.run()
