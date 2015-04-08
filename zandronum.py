#from PyQt4 import QtCore
from huffman import Huffman;
from bytestream import ByteStream;
#from data import settings;
from threading import Thread;
import time;
import copy;
import sys;

#from ip2country import ip2country;

import socket;
import select;

class ServerListColumn:
    Flags       = 0;
    Players     = 1;
    Ping        = 2;
    Title       = 3;
    Address     = 4;
    IWAD        = 5;
    Map         = 6;
    PWADs       = 7;
    GameMode    = 8;

class ZandronumPacketId:
    LAUNCHER_MASTER_CHALLENGE   = 5660028;
    MSC_IPISBANNED              = 3;
    MSC_REQUESTIGNORED          = 4;
    MSC_WRONGVERSION            = 5;
    MSC_BEGINSERVERLISTPART     = 6;
    MSC_SERVERBLOCK             = 8;
    MSC_ENDSERVERLIST           = 2;
    MSC_ENDSERVERLISTPART       = 7;
    LAUNCHER_CHALLENGE          = 199;
    SERVER_IPISBANNED           = 5660025;
    SERVER_REQUESTIGNORED       = 5660024;
    SERVER_REPLY                = 5660023;

class ZandronumQuery:
    SQF_NAME                = 0x00000001;
    SQF_URL                 = 0x00000002;
    SQF_EMAIL               = 0x00000004;
    SQF_MAPNAME             = 0x00000008;
    SQF_MAXCLIENTS          = 0x00000010;
    SQF_MAXPLAYERS          = 0x00000020;
    SQF_PWADS               = 0x00000040;
    SQF_GAMETYPE            = 0x00000080;
    SQF_GAMENAME            = 0x00000100;
    SQF_IWAD                = 0x00000200;
    SQF_FORCEPASSWORD       = 0x00000400;
    SQF_FORCEJOINPASSWORD   = 0x00000800;
    SQF_GAMESKILL           = 0x00001000;
    SQF_BOTSKILL            = 0x00002000;
    SQF_DMFLAGS             = 0x00004000;
    SQF_LIMITS              = 0x00010000;
    SQF_TEAMDAMAGE          = 0x00020000;
    SQF_TEAMSCORES          = 0x00040000;
    SQF_NUMPLAYERS          = 0x00080000;
    SQF_PLAYERDATA          = 0x00100000;
    SQF_TEAMINFO_NUMBER     = 0x00200000;
    SQF_TEAMINFO_NAME       = 0x00400000;
    SQF_TEAMINFO_COLOR      = 0x00800000;
    SQF_TEAMINFO_SCORE      = 0x01000000;
    SQF_TESTING_SERVER      = 0x02000000;
    SQF_DATA_MD5SUM         = 0x04000000;
    SQF_ALL_DMFLAGS         = 0x08000000;
    SQF_SECURITY_SETTINGS   = 0x10000000;

class ZandronumFlags:
    mDMFlags = {0x00000001:        "Disallow health",
                0x00000002:        "Disallow powerups",
                0x00000004:        "Weapons stay",
                0x00000008:        "Falling damage (ZDoom)",
                0x00000010:        "Falling damage (Hexen)",
                0x00000018:        "Falling damage (Strife)",
                0x00000020:        "<ERROR>",
                0x00000040:        "No map change on exit",
                0x00000080:        "Spawn farthest (DM)",
                0x00000100:        "Force respawn (DM)",
                0x00000200:        "Disallow armor",
                0x00000400:        "Suicide on exit",
                0x00000800:        "Infinite ammo",
                0x00001000:        "No monsters",
                0x00002000:        "Monsters respawn",
                0x00004000:        "Items respawn",
                0x00008000:        "Fast monsters",
                0x00010000:        "Jump disabled",
                0x00020000:        "Freelook disabled",
                0x00040000:        "Mega powerups respawn",
                0x00080000:        "No FOV change",
                0x00100000:        "No multiplayer weapons",
                0x00200000:        "Crouch disabled",
                0x00400000:        "Lose inventory on death (Coop)",
                0x00800000:        "Lose keys on death (Coop)",
                0x01000000:        "Lose weapons on death (Coop)",
                0x02000000:        "Lose armor on death (Coop)",
                0x04000000:        "Lose powerups on death (Coop)",
                0x08000000:        "Lose ammo on death (Coop)",
                0x10000000:        "Lose half of ammo on death (Coop)",
                0x20000000:        "Jump enabled",
                0x40000000:        "Crouch enabled"};
    
    mDMFlags2 ={0x00000001:        "<ERROR>",
                0x00000002:        "Drop weapon on death",
                0x00000004:        "Runes disabled",
                0x00000008:        "Instant flag return (ST/CTF)",
                0x00000010:        "No team switching (ST/CTF)",
                0x00000020:        "Random teams (ST/CTF)",
                0x00000040:        "Double ammo from pickups",
                0x00000080:        "Degeneration",
                0x00000100:        "Allow BFG freelook",
                0x00000200:        "Barrels respawn",
                0x00000400:        "No respawn protection",
                0x00000800:        "Start with Shotgun (Coop)",
                0x00001000:        "Respawn where died (Coop)",
                0x00002000:        "Keep teams on map change",
                0x00004000:        "Keep frags on map change",
                0x00008000:        "Respawn disabled",
                0x00010000:        "Players lose a frag on death",
                0x00020000:        "Infinite inventory",
                0x00040000:        "Force OpenGL defaults",
                0x00080000:        "Rocketjumping disabled",
                0x00100000:        "Count damage instead of kills (Coop)",
                0x00200000:        "Alpha enabled/forced",
                0x00400000:        "Kill all monsters to exit (Coop)",
                0x00800000:        "No automap",
                0x01000000:        "No allies on automap",
                0x02000000:        "No coop spy",
                0x04000000:        "Chasecam enabled",
                0x08000000:        "No suiciding",
                0x10000000:        "No autoaim",
                0x20000000:        "Only spawn singleplayer things (Coop)"};
    
    mDMFlags3 ={0x00000001:        "Don't show nicknames of players under crosshair",
                0x00000002:        "Force LMS spectator settings",
                0x00000004:        "No coop info",
                0x00000008:        "No unlagged",
                0x00000010:        "Unblock players",
                0x00000020:        "No medals"};
    
    mCpFlags = {0x00000001:        "Find shortest textures like Doom",
                0x00000002:        "Use buggier stair building",
                0x00000004:        "Limit pain elementals to 20 lost souls",
                0x00000008:        "Don't let others hear pickups",
                0x00000010:        "Actors are infinitely tall",
                0x00000020:        "Allow silent BFG trick",
                0x00000040:        "Enable wallrunning",
                0x00000080:        "Spawn item drops on the floor",
                0x00000100:        "All special lines can block use lines",
                0x00000200:        "Disable Boom door light effect",
                0x00000400:        "Raven's scrollers use original speed",
                0x00000800:        "Use sector based sound target code",
                0x00001000:        "Limit deh.MaxHealth to health bonus",
                0x00002000:        "Trace ignores lines w/same sector on both sides",
                0x00004000:        "No monster dropoff move",
                0x00008000:        "Scrolling sectors are additive",
                0x00010000:        "Monsters see semi-invisible players",
                0x00020000:        "Limited movement in the air",
                0x00040000:        "Enable plasma bump",
                0x00080000:        "Allow instant respawn",
                0x00100000:        "Disable taunts",
                0x00200000:        "Original sound curve",
                0x00400000:        "Use old intermission screens/music",
                0x00800000:        "Disable stealth monsters",
                0x01000000:        "Old radius damage",
                0x02000000:        "Disable crosshair",
                0x04000000:        "Old weapon switch",
                0x08000000:        "Silent instant floors",
                0x10000000:        "Sector sounds",
                0x20000000:        "Doom missile clip",
                0x40000000:        "Monster drop off"};
    
    mCpFlags2 ={0x00000001:        "NET scripts are clientside",
                0x00000002:        "Clients send full button info",
                0x00000004:        "'land' CCMD disabled",
                0x00000008:        "Old random generator",
                0x00000010:        "NOGRAVITY spheres",
                0x00000020:        "Don't stop player scripts on disconnect",
                0x00000040:        "Old explosion thrust",
                0x00000080:        "Old bridge drops",
                0x00000100:        "Old jump physics",
                0x00000200:        "No weapon switch cancellation"};

class ZandronumPacket(ByteStream):
    def encode(self, encoder):
        self.position_read = 0;
        self.position_write = 0;
        self.buffer = bytearray(encoder.encode(self.buffer));
    
    def decode(self, decoder):
        self.position_read = 0;
        self.position_write = 0;
        self.buffer = bytearray(decoder.decode(self.buffer));

class ZandronumGameMode:
    Cooperative = 0;
    Survival    = 1;
    Invasion    = 2;
    Deathmatch  = 3;
    TeamDM      = 4;
    Duel        = 5;
    Terminator  = 6;
    LMS         = 7;
    TeamLMS     = 8;
    Possession  = 9;
    TeamPossession = 10;
    TeamGame    = 11;
    CTF         = 12;
    OneFlagCTF  = 13;
    Skulltag    = 14;
    Domination  = 15;

class ZandronumPlayer:
    def __init__(self, name, points, ping, spectator, bot, team, time):
        self.name = name;
        self.points = points;
        self.ping = ping;
        self.spectator = spectator;
        self.bot = bot;
        self.team = team if (team >= 0 and team <= 254) else -1;
        self.time = time;
    
    def clean_name(self):
        name = '';
        i = 0;
        skipping = False;
        while True:
            if i >= len(self.name):
                break;
            if not skipping:
                if self.name[i] == '\x1C':
                    i += 1;
                    if self.name[i] == '[':
                        skipping = True;
                    i += 1;
                    continue;
                name += self.name[i];
                i += 1;
            else:
                if self.name[i] == ']':
                    skipping = False;
                    i += 1;
                    continue;
                i += 1;
        return name;
    
    def __lt__(self, other):
        return self.points > other.points;

class ZandronumTeam:
    def __init__(self):
        self.name = '';
        self.color = 0;
        self.score = 0;

class ZandronumServer:
    def reset(self):
        self.addr_octets = (0, 0, 0, 0);
        self.addr = (None, None);
        self.title = "";
        self.game_mode = None;
        self.iwad = "";
        self.pwads = [];
        self.ping = 0;
        self.version = "";
        self.instagib = False;
        self.buckshot = False;
        self.sort_column = ServerListColumn.Title;
        self.level = "";
        self.maxclients = 0;
        self.maxplayers = 0;
        self.numplayers = 0;
        self.players = [];
        self.forcepassword = False;
        self.forcejoinpassword = False;
        self.hidden = False;
        self.country = None;
        self.country_name = '';
        self.pwads = [];
        self.na = True;
        self.refreshing = False;
        self.last_refresh_frame = 0;
        self.teams = [];
        self.skill = 0;
        self.game_name = '';
        self.fraglimit = 0;
        self.timelimit = 0;
        self.timeleft = 0;
        self.duellimit = 0;
        self.pointlimit = 0;
        self.winlimit = 0;
        self.dmflags = 0;
        self.dmflags2 = 0;
        self.dmflags3 = 0;
        self.compatflags = 0;
        self.compatflags2 = 0;
    
    def __init__(self):
        self.reset();
    
    def point_name(self):
        if (self.game_mode == ZandronumGameMode.Deathmatch or
            self.game_mode == ZandronumGameMode.TeamDM or
            self.game_mode == ZandronumGameMode.Duel or
            self.game_mode == ZandronumGameMode.Terminator or
            self.game_mode == ZandronumGameMode.LMS):
                return 'Frag';
        elif (self.game_mode == ZandronumGameMode.CTF or
            self.game_mode == ZandronumGameMode.OneFlagCTF):
                return 'Flag';
        elif (self.game_mode == ZandronumGameMode.Cooperative or
            self.game_mode == ZandronumGameMode.Survival or
            self.game_mode == ZandronumGameMode.Invasion):
                return 'Kill';
        return 'Point';
    
    def is_team_game(self):
        return (self.game_mode == ZandronumGameMode.TeamDM or
                self.game_mode == ZandronumGameMode.TeamLMS or
                self.game_mode == ZandronumGameMode.TeamPossession or
                self.game_mode == ZandronumGameMode.TeamGame or
                self.game_mode == ZandronumGameMode.CTF or
                self.game_mode == ZandronumGameMode.OneFlagCTF or
                self.game_mode == ZandronumGameMode.Skulltag); # is domination using teams?..
    
    def game_mode_as_string(self):
        for key in ZandronumGameMode.__dict__:
            if key[0:2] == '__':
                continue;
            if ZandronumGameMode.__dict__[key] == self.game_mode:
                return key;
        return "";
    
    def address_as_long(self):
        l = 0x00000000;
        for octet in self.addr_octets:
            l <<= 8;
            l |= octet;
        return l;
    
    def skill_as_string(self):
        skills_doom = ["I'm too young to die", "Hey, not too rough", "Hurt me plenty", "Ultra-Violence", "Nightmare!"];
        skills_htic = ["Thou needeth a wet-nurse", "Yellowbellies-r-us", "Bringest them oneth", "Thou art a smite-meister", "Black plague possesses thee"];
        skills_hexen = ["Squire / Altar boy / Apprentice", "Knight / Acolyte / Enchanter", "Warrior / Priest / Sorcerer", "Berserker / Cardinal / Warlock", "Titan / Pope / Archimage"];
        sk_str = 'Unknown';
        if self.skill >= 0 and self.skill < 5:
            if self.game_name.upper() == 'HERETIC':
                sk_str = skills_htic[self.skill];
            elif self.game_name.upper() == 'HEXEN':
                sk_str = skills_hexen[self.skill];
            else:
                sk_str = skills_doom[self.skill];
        return sk_str;
    
    def compare_string(self, string1, string2):
        if (string1 == "" or string1 is None) and (string2 == "" or string2 == None):
            return True;
        if (string1 == "" or string1 is None) and (string2 != "" and string2 != None):
            return True;
        if (string1 != "" and string1 != None) and (string2 == "" or string2 == None):
            return False;
        return string1 < string2;
    
    def compare_address(self, other):
        if other.addr[0] is None and self.addr[0] is None:
            return True;
        if other.addr[0] is None and self.addr[0] is not None:
            return True;
        if other.addr[0] is not None and self.addr[0] is None:
            return False;
        if self.address_as_long() == other.address_as_long():
            return self.addr[1] < other.addr[1];
        return self.address_as_long() < other.address_as_long();
    
    # sorting by unimplemented columns is currently just random
    # returns less-than (True/False)
    def compare(self, other):
        if (other.ping == 0 and self.ping == 0) or\
            (other.na and not other.title and self.na and not self.title) or\
            (other.game_mode is None and self.game_mode is None):
                return self.compare_address(other);
        if self.sort_column == ServerListColumn.Ping:
            if other.ping == 0 and self.ping == 0:
                return True;
            if other.ping == 0 and self.ping != 0:
                return True;
            if other.ping != 0 and self.ping == 0:
                return False;
            return self.ping < other.ping;
        elif self.sort_column == ServerListColumn.Title:
            return self.compare_string(self.title, other.title);
        elif self.sort_column == ServerListColumn.Address:
            return self.compare_address(other);
        elif self.sort_column == ServerListColumn.IWAD:
            return self.compare_string(self.iwad, other.iwad);
        elif self.sort_column == ServerListColumn.Map:
            return self.compare_string(self.level, other.level);
        elif self.sort_column == ServerListColumn.GameMode:
            return self.compare_string(self.game_mode_as_string(), other.game_mode_as_string());
        return False;
    
    def __lt__(self, other):
        if self.sort_players:
            if len(self.players) > 0 and len(other.players) <= 0:
                return True;
            if len(self.players) <= 0 and len(other.players) > 0:
                return False;
        desc = False
        if desc:
            return self.compare(other);
        return not self.compare(other);

class ZandronumRefresherThreadConfig:
    def __init__(self):
        self.exiting = False;
        self.refresher = None;
        self.master = True;

def refresherThread(config):
    # k start refreshing
    _servers = [];
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    try:
        huff = Huffman();
        sock.bind(("0.0.0.0", 0));
        sock.setblocking(0);
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32768000);
        # master ip = "master.zandronum.com", 15300
        
        masterTimeout = 5#settings.GetFloat("pyl.browser.timeout_master") / 1000.0;
        serversTimeout = 5#settings.GetFloat("pyl.browser.timeout_servers") / 1000.0;
        
        #ip2c = ip2country.IP2Country();
        #if not ip2c.load_from_dat("%s/ip2country/GeoIPCountryWhois.dat" % (sys.mybase)):
        #    print("refresh: Failed to initialize IP2C database. Country resolving will be unavailable.");
        #    ip2c = None;
        ip2c = None
        
        refStart = time.time();
        
        if config.master:
            master_ip = ('master.zandronum.com', 15300)#(settings.Get("pyl.browser.master_address"), settings.GetInt("pyl.browser.master_port"));
            pack = ZandronumPacket();
            pack.write_uint32(ZandronumPacketId.LAUNCHER_MASTER_CHALLENGE);
            pack.write_uint32(2);
            pack.encode(huff);
            
            try:
                print("refresh: Sent master server request...");
                sock.sendto(pack.buffer, master_ip);
            except:
                print("refresh: Failed to query master server.");
                _servers = config.refresher.old_servers;
                return;
            
            packets = [];
            have_last = False;
            last_id = -1;
            
            startTime = time.time();
            upTime = time.time();
            #config.refresher.signalProgress.emit('Getting master server list...', int(startTime*1000), int((startTime+masterTimeout)*1000), int(time.time()*1000));
            while time.time()-startTime <= masterTimeout:
                #config.refresher.signalProgress.emit('test', 0, 0);
                if time.time()-upTime > 0.5:
                    #config.refresher.signalProgress.emit('Getting master server list...', int(startTime*1000), int((startTime+masterTimeout)*1000), int(time.time()*1000));
                    upTime = time.time();
                try:
                    cReadyRead, cReadyWrite, cError = select.select([sock], [], [], 0.0);
                    if sock not in cReadyRead:
                        continue;
                    pack.reset();
                    (pack.buffer, out_addr) = sock.recvfrom(10240);
                except socket.timeout:
                    print("refresh: Master server timeout hit.");
                    _servers = config.refresher.old_servers;
                    break;
                except:
                    print("refresh: Error on receiving packet from the master server.");
                    _servers = config.refresher.old_servers;
                    return;
                pack.decode(huff);
                response = pack.read_uint32();
                if response == ZandronumPacketId.MSC_IPISBANNED:
                    print("refresh: Your IP is banned.");
                    _servers = config.refresher.old_servers;
                    return;
                elif response == ZandronumPacketId.MSC_REQUESTIGNORED:
                    print("refresh: Your IP has made a request in the past 3 seconds.");
                    _servers = config.refresher.old_servers;
                    break;
                elif response == ZandronumPacketId.MSC_WRONGVERSION:
                    print("refresh: You're using an older version of the master procotol.");
                    _servers = config.refresher.old_servers;
                    return;
                elif response == ZandronumPacketId.MSC_BEGINSERVERLISTPART:
                    p_id = pack.read_uint8();
                    print("refresh: Accepted server list part #%d." % (p_id));
                    if p_id in packets:
                        print("refresh: Received duplicate list part #%d." % (p_id));
                        continue;
                    packets.append(p_id);
                    serverblock = pack.read_uint8();
                    if serverblock != ZandronumPacketId.MSC_SERVERBLOCK:
                        print("refresh: Received malformed list part #%d; expected MSC_SERVERBLOCK, got 0x%02X." % (p_id, serverblock));
                        continue;
                    servercount = pack.read_uint8();
                    while servercount != 0:
                        oct_1 = pack.read_uint8();
                        oct_2 = pack.read_uint8();
                        oct_3 = pack.read_uint8();
                        oct_4 = pack.read_uint8();
                        _ip = "%d.%d.%d.%d" % (oct_1, oct_2, oct_3, oct_4);
                        country = None;
                        if ip2c is not None:
                            country = ip2c.resolve_ip(_ip);
                        for i in range(0, servercount):
                            port = pack.read_uint16();
                            server = ZandronumServer();
                            server.addr = (_ip, port);
                            server.country = country;
                            server.refresh_start = refStart;
                            server.refreshing = True;
                            if country is not None:
                                server.flag = server.country[0].lower();
                            else:
                                server.flag = None;
                            server.addr_octets = (oct_1, oct_2, oct_3, oct_4);
                            _servers.append(server);
                        servercount = pack.read_uint8();
                    end = pack.read_uint8();
                    if end == ZandronumPacketId.MSC_ENDSERVERLIST:
                        have_last = True;
                        last_id = p_id;
                        break;
                    elif end != ZandronumPacketId.MSC_ENDSERVERLISTPART:
                        print("refresh: Received malformed list part #%d; expected MSC_ENDSERVERLIST or MSC_ENDSERVERLISTPART, got 0x%02X." % (p_id, end));
                        continue;
                else:
                    print("refresh: Received malformed packet; expected MSC_IPISBANNED, MSC_REQUESTIGNORED, MSC_BEGINSERVERLISTPART or MSC_SERVERBLOCK; got 0x%08X." % (response));
                    continue;
            if last_id == -1:
                print("refresh: Last packet got lost. Estimating last packet ID from largest number.");
                for _id in packets:
                    if _id > last_id:
                        last_id = _id;
            for _id in range(0, last_id+1):
                if _id not in packets:
                    print("refresh: Packet #%d got lost. Servers from this part will be unavailable." % (_id));
            config.refresher.servers = copy.deepcopy(_servers);
        else:
            _servers = config.new_servers;
            for server in _servers:
                server.refreshing = True;
                server.refresh_start = time.time();
        print("refresh: Querying individual servers...");
        for server in _servers:
            server._raw_buffer = None;
            server._raw_ping = 0.0;
        def queryThread(_servers, sock):
            for server in _servers:
                #print("%s:%d" % (server.addr[0], server.addr[1]));
                server._raw_ping = time.time();
                pack = ZandronumPacket();
                pack.write_uint32(ZandronumPacketId.LAUNCHER_CHALLENGE);
                flags = 0;
                flags |= ZandronumQuery.SQF_NAME;
                flags |= ZandronumQuery.SQF_GAMETYPE;
                flags |= ZandronumQuery.SQF_IWAD;
                flags |= ZandronumQuery.SQF_MAPNAME;
                flags |= ZandronumQuery.SQF_MAXCLIENTS;
                flags |= ZandronumQuery.SQF_MAXPLAYERS;
                flags |= ZandronumQuery.SQF_NUMPLAYERS;
                flags |= ZandronumQuery.SQF_PLAYERDATA;
                flags |= ZandronumQuery.SQF_FORCEPASSWORD;
                flags |= ZandronumQuery.SQF_FORCEJOINPASSWORD;
                flags |= ZandronumQuery.SQF_PWADS;
                flags |= ZandronumQuery.SQF_TEAMINFO_NUMBER;
                flags |= ZandronumQuery.SQF_TEAMINFO_NAME;
                flags |= ZandronumQuery.SQF_TEAMINFO_COLOR;
                flags |= ZandronumQuery.SQF_TEAMINFO_SCORE;
                flags |= ZandronumQuery.SQF_GAMESKILL;
                flags |= ZandronumQuery.SQF_GAMENAME;
                flags |= ZandronumQuery.SQF_LIMITS;
                flags |= ZandronumQuery.SQF_ALL_DMFLAGS;
                pack.write_uint32(flags);
                pack.write_uint32(0);
                pack.encode(huff);
                try:
                    sock.sendto(pack.buffer, server.addr);
                except:
                    print("refresh: Failed to query server %s:%d." % (server.addr[0], server.addr[1]));
        queryT = Thread(target=queryThread, args=(_servers, sock));
        queryT.daemon = True;
        queryT.start();
        startTime = time.time();
        sock.setblocking(0);
        tSS = 0;
        recvd2 = [None] * len(_servers);
        recvd1 = 0;
        queryLeft = len(_servers);
        upTime = time.time();
        #config.refresher.signalProgress.emit('Refreshing servers...', int(startTime*1000), int((startTime+serversTimeout)*1000), int(time.time()*1000));
        while (time.time()-startTime <= serversTimeout) and (queryLeft > 0):
            if time.time()-upTime > 0.5:
                #config.refresher.signalProgress.emit('Refreshing servers...', int(startTime*1000), int((startTime+serversTimeout)*1000), int(time.time()*1000));
                upTime = time.time();
            server = None;
            cT = time.time();
            try:
                cReadyRead, cReadyWrite, cError = select.select([sock], [], [], 0.0);
                if sock not in cReadyRead:
                    continue;
                (_raw_buffer, out_addr) = sock.recvfrom(65536);
            except socket.timeout:
                print("refresh: Server receive timeout hit.");
                continue;
            except:
                print("refresh: Error on receiving packet from the server.");
                continue;
            recvd2[recvd1] = (out_addr, cT, _raw_buffer);
            recvd1 += 1;
            queryLeft -= 1;
            #print("time spent on searching: %f" % (time.time()-cT));
            tSS += time.time()-cT;
        for recvd in recvd2:
            if recvd is None:
                continue;
            out_addr = recvd[0];
            _raw_buffer = recvd[2];
            cT = recvd[1];
            for _server in _servers:
                if _server.addr[0] == out_addr[0] and _server.addr[1] == out_addr[1]:
                    server = _server;
                    break;
            if server is None:
                print("refresh: Received packet from uknown server %s:%d." % (out_addr[0], out_addr[1]));
                continue;
            if server._raw_buffer is not None:
                print("refresh: Received duplicate packet from server %s:%d." % (out_addr[0], out_addr[1]));
                continue;
            server._raw_buffer = (cT-server._raw_ping, _raw_buffer);
        for server in _servers:
            #print("refresh: _: Processing %s:%d." % (server.addr[0], server.addr[1]));
            if server._raw_buffer is not None:
                server.ping = int(server._raw_buffer[0]*1000);
                try:
                    pack = ZandronumPacket();
                    pack.buffer = server._raw_buffer[1];
                    pack.decode(huff);
                    response = pack.read_uint32();
                    if response == ZandronumPacketId.SERVER_IPISBANNED:
                        server.na = True;
                        server.refreshing = False;
                        print("refresh: Your IP is banned (on server %s:%d)." % (server.addr[0], server.addr[1]));
                        continue;
                    elif response == ZandronumPacketId.SERVER_REQUESTIGNORED:
                        server.na = True;
                        server.refreshing = False;
                        print("refresh: Your IP has made a request in the past 3 seconds (on server %s:%d)." % (server.addr[0], server.addr[1]));
                        continue;
                    elif response == ZandronumPacketId.SERVER_REPLY:
                        server.na = False;
                        _time = pack.read_uint32();
                        server.version = pack.read_string();
                        flags = pack.read_uint32();
                        if (flags & ZandronumQuery.SQF_NAME) == ZandronumQuery.SQF_NAME:
                            server.title = pack.read_string();
                        if (flags & ZandronumQuery.SQF_MAPNAME) == ZandronumQuery.SQF_MAPNAME:
                            server.level = pack.read_string();
                        if (flags & ZandronumQuery.SQF_MAXCLIENTS) == ZandronumQuery.SQF_MAXCLIENTS:
                            server.maxclients = pack.read_uint8();
                        if (flags & ZandronumQuery.SQF_MAXPLAYERS) == ZandronumQuery.SQF_MAXPLAYERS:
                            server.maxplayers = pack.read_uint8();
                        if (flags & ZandronumQuery.SQF_PWADS) == ZandronumQuery.SQF_PWADS:
                            pwad_count = pack.read_uint8();
                            for i in range(0, pwad_count):
                                server.pwads.append(pack.read_string());
                        if (flags & ZandronumQuery.SQF_GAMETYPE) == ZandronumQuery.SQF_GAMETYPE:
                            server.game_mode = pack.read_uint8();
                            server.instagib = pack.read_uint8() != 0;
                            server.buckshot = pack.read_uint8() != 0;
                        if (flags & ZandronumQuery.SQF_GAMENAME) == ZandronumQuery.SQF_GAMENAME:
                            server.game_name = pack.read_string();
                        if (flags & ZandronumQuery.SQF_IWAD) == ZandronumQuery.SQF_IWAD:
                            server.iwad = pack.read_string();
                        if (flags & ZandronumQuery.SQF_FORCEPASSWORD) == ZandronumQuery.SQF_FORCEPASSWORD:
                            server.forcepassword = pack.read_uint8() != 0;
                        if (flags & ZandronumQuery.SQF_FORCEJOINPASSWORD) == ZandronumQuery.SQF_FORCEJOINPASSWORD:
                            server.forcejoinpassword = pack.read_uint8() != 0;
                        if (flags & ZandronumQuery.SQF_GAMESKILL) == ZandronumQuery.SQF_GAMESKILL:
                            server.skill = pack.read_uint8();
                        if (flags & ZandronumQuery.SQF_LIMITS) == ZandronumQuery.SQF_LIMITS:
                            server.fraglimit = pack.read_uint16();
                            server.timelimit = pack.read_uint16();
                            if server.timelimit > 0:
                                server.timeleft = pack.read_uint16();
                            server.duellimit = pack.read_uint16();
                            server.pointlimit = pack.read_uint16();
                            server.winlimit = pack.read_uint16();
                        if (flags & ZandronumQuery.SQF_NUMPLAYERS) == ZandronumQuery.SQF_NUMPLAYERS:
                            server.numplayers = pack.read_uint8();
                            server.players = [None] * server.numplayers;
                        if (flags & ZandronumQuery.SQF_PLAYERDATA) == ZandronumQuery.SQF_PLAYERDATA:
                            _player = 0;
                            for i in range(0, server.numplayers):
                                server.players[_player] = ZandronumPlayer(pack.read_string(),
                                                                        pack.read_int16(),
                                                                        pack.read_uint16(), # should probably read int here to display the same negative value as the server itself?
                                                                        pack.read_uint8() != 0,
                                                                        pack.read_uint8() != 0,
                                                                        pack.read_uint8() if server.is_team_game() else 255,
                                                                        pack.read_uint8());
                                _player += 1;
                        if (flags & ZandronumQuery.SQF_TEAMINFO_NUMBER) == ZandronumQuery.SQF_TEAMINFO_NUMBER:
                            _teams = pack.read_uint8();
                            for i in range(0, _teams):
                                server.teams.append(ZandronumTeam());
                        if (flags & ZandronumQuery.SQF_TEAMINFO_NAME) == ZandronumQuery.SQF_TEAMINFO_NAME:
                            for i in range(0, len(server.teams)):
                                server.teams[i].name = pack.read_string();
                        if (flags & ZandronumQuery.SQF_TEAMINFO_COLOR) == ZandronumQuery.SQF_TEAMINFO_COLOR:
                            for i in range(0, len(server.teams)):
                                server.teams[i].color = pack.read_uint32();
                        if (flags & ZandronumQuery.SQF_TEAMINFO_SCORE) == ZandronumQuery.SQF_TEAMINFO_SCORE:
                            for i in range(0, len(server.teams)):
                                server.teams[i].score = pack.read_int16();
                        if (flags & ZandronumQuery.SQF_ALL_DMFLAGS) == ZandronumQuery.SQF_ALL_DMFLAGS:
                            flagsCount = pack.read_uint8();
                            if flagsCount != 5:
                                raise ValueError;
                            server.dmflags = pack.read_uint32();
                            server.dmflags2 = pack.read_uint32();
                            server.dmflags3 = pack.read_uint32();
                            server.compatflags = pack.read_uint32();
                            server.compatflags2 = pack.read_uint32();
                        server.na = False;
                        server.refreshing = False;
                    else:
                        server.na = True;
                        server.refreshing = False;
                        print("refresh: Received malformed packet from server %s:%d; expected SERVER_IPISBANNED, SERVER_REQUESTIGNORED or SERVER_REPLY, got 0x%08X." % (server.addr[0], server.addr[1], response));
                        continue;
                except Exception as ex:
                    print("refresh: Caught exception while parsing packet from server %s:%d." % (server.addr[0], server.addr[1]));
                    ex2 = sys.exc_info();
                    sys.excepthook(ex2[0], ex, ex2[2]);
                    ping = server.ping;
                    addr = server.addr;
                    c = server.country;
                    c_name = server.country_name;
                    server.reset();
                    server.country = c;
                    server.country_name = c_name;
                    server.addr = addr;
                    server.na = True;
                    server.refreshing = False;
                    server.hidden = False;
                    server.ping = ping;
                    server.title = "<<< BAD PACKET DATA >>>";
                    continue;
        for server in _servers:
            server.refreshing = False;
        print("refresh: Finished querying individual servers.");
    finally:
        #config.refresher.signalProgress.emit('', 0, 0, 0);
        if config.master:
            config.refresher.servers = copy.deepcopy(_servers);
            _i = 0;
            for _server in _servers:
                if not _server.na:
                    _i += 1;
                    continue;
                for server in config.refresher.old_servers:
                    if server.na:
                        continue;
                    if server.addr[0] == _server.addr[0] and server.addr[1] == server.addr[1]:
                        _servers[_i] = server;
                        server.na = True;
                        break;
                _i += 1;
        try:
            sock.close();
        except:
            pass;

class ZandronumRefresher:
    def __init__(self):
        self.servers = [];
        self.old_servers = None;
    
    def refresh(self):
        self.old_servers = self.servers;
        self.servers = [];
        config = ZandronumRefresherThreadConfig();
        config.refresher = self;
        thread = Thread(target=refresherThread, args=(config,));
        thread.daemon = True;
        thread.start();
    
    def refreshOne(self, server):
        self.new_servers = [server];
        config = ZandronumRefresherThreadConfig();
        config.refresher = self;
        config.new_servers = self.new_servers;
        config.master = False;
        thread = Thread(target=refresherThread, args=(config,));
        thread.daemon = True;
        thread.start();
    
    def visible_count(self):
        cnt = 0;
        for server in self.servers:
            if server is None:
                continue;
            if server.hidden:
                continue;
            cnt += 1;
        return cnt;
