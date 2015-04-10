# -*- coding: utf-8 -*-# Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn.import jsonimport timeimport structimport ctypeskernel = ctypes.windll.kernel32import subprocessimport sysdef dhex(what):    s = []    for c in what:        s.append('%02X' % c)    return ' '.join(s)    def dhexfile(what, filename):    try:        with open(filename, 'wb') as f:            f.write(what)    except:        passclass Process(object):    def __init__(self, pid):        global kernel        self.pid = pid        self.h = kernel.OpenProcess(0x0018, 0, pid)            def close(self):        global kernel        if (self.h and kernel is not None):            kernel.CloseHandle(self.h)        self.h = None            def __del__(self):        self.close()            def read(self, addr, size):        global kernel        buf = ctypes.create_string_buffer(size)        bytesread = ctypes.c_size_t()        kernel.ReadProcessMemory(self.h, addr, buf,        ctypes.c_size_t(size),        ctypes.addressof(bytesread))        return bytearray(buf[:bytesread.value])            def read_dword(self, addr):        return struct.unpack('<I', self.read(addr, 4))[0]            def read_word(self, addr):        return struct.unpack('<H', self.read(addr, 2))[0]            def read_byte(self, addr):        return self.read(addr, 1)[0]            def read_nullterm(self, addr):        s = ''        while True:            c = self.read_byte(addr)            if c > 0:                s += chr(c)                addr += 1                continue            break        return s            def read_nullterm_unicode(self, addr):        s = u''        while True:            c = self.read_word(addr)            if c > 0:                s += unichr(c)                addr += 2                continue            break        return s                class DEXParser:    def __init__(self, dir='.'):        startupinfo = subprocess.STARTUPINFO()        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW        startupinfo.wShowWindow = subprocess.SW_HIDE        self.hProcess = subprocess.Popen('%s/DoomExplorer.exe'%dir, startupinfo=startupinfo)        self.pMemory = Process(self.hProcess.pid)        self.servers = []        self.dir = dir    def refresh(self):        if self.hProcess.poll() is not None:            print('Resetting refresher...')            self.__init__(self.dir)            time.sleep(10.0)        #print('Reading servers...')            hProcess = self.hProcess        pMemory = self.pMemory        StaticListRef = 0x92D628        #dhexfile(StaticList, 'StaticList')        #staticlist+48+i*4 = infolist theoretically        Ports = ['od', 'zd', 'za']        Servers = []        for i in range(3):            # 0 = od            # 1 = zd            # 2 = za                        ServersOff = len(Servers)                        NetAddrListRef = pMemory.read_dword(StaticListRef+i*4)            NetAddrListObjects = pMemory.read_dword(NetAddrListRef+4)            NetAddrListCount = pMemory.read_dword(NetAddrListRef+8)            for j in range(NetAddrListCount):                NetAddrRef = pMemory.read_dword(NetAddrListObjects+j*4)                # 0x80 is the size?                NetAddr = pMemory.read(NetAddrRef, 0x80)                #dhexfile(NetAddr, 'NetAddr%d'%j)                                NA_Ip = '%d.%d.%d.%d' % (NetAddr[8], NetAddr[9], NetAddr[10], NetAddr[11])                NA_Port = struct.unpack('<I', NetAddr[12:16])[0]                                NA_Unk0, NA_Unk1, NA_Unk2 = struct.unpack('<III', NetAddr[0x44:0x50])                NA_Unk3, NA_Unk4 = struct.unpack('<II', NetAddr[0x54:0x5C])                NA_Unk5 = struct.unpack('<I', NetAddr[0x60:0x64])[0]                NA_Unk6 = struct.unpack('<I', NetAddr[0x7C:0x80])[0]                                #dhexfile(pMemory.read(NA_Unk0, 64), 'NetAddr%d_Unk0'%j) # IP as string                #dhexfile(pMemory.read(NA_Unk1, 64), 'NetAddr%d_Unk1'%j) # ???                #dhexfile(pMemory.read(NA_Unk2, 64), 'NetAddr%d_Unk2'%j) # Country name (full)                #dhexfile(pMemory.read(NA_Unk3, 64), 'NetAddr%d_Unk3'%j) # Country abbreviation                #dhexfile(pMemory.read(NA_Unk4, 64), 'NetAddr%d_Unk4'%j) # ???                #dhexfile(pMemory.read(NA_Unk5, 64), 'NetAddr%d_Unk5'%j) # Country name unicode                #dhexfile(pMemory.read(NA_Unk6, 64), 'NetAddr%d_Unk6'%j) # ???                                NA_CountryName = pMemory.read_nullterm_unicode(NA_Unk5)                                # todo: build list                Server = {'port': Ports[i], 'ip': '%s:%d' % (NA_Ip, NA_Port), 'country': NA_CountryName}                Servers.append(Server)                            InfoListRef = pMemory.read_dword(StaticListRef+48+i*4)            InfoListObjects = pMemory.read_dword(InfoListRef+4)            InfoListCount = pMemory.read_dword(InfoListRef+8)            for j in range(InfoListCount):                InfoRef = pMemory.read_dword(InfoListObjects+j*4)                j += ServersOff                # size unknown                Info = pMemory.read(InfoRef, 256)                #print('Server = %s' % (Servers[j]['ip']))                                I_Unk0 = struct.unpack('<I', Info[0:4])[0] # name? // nope                I_Unk1 = struct.unpack('<I', Info[0x1C:0x20])[0] # VERSION                I_Unk2 = struct.unpack('<I', Info[0x20:0x24])[0] # name                I_Unk3 = struct.unpack('<I', Info[0x24:0x28])[0] # email                I_Unk4 = struct.unpack('<I', Info[0x28:0x2C])[0] # mailto:email                I_Unk5 = struct.unpack('<I', Info[0x2C:0x30])[0] # wadurl                I_Unk6 = struct.unpack('<I', Info[0x30:0x34])[0] # wadurl                I_Unk7 = struct.unpack('<I', Info[0x34:0x38])[0] # game name                I_Unk8 = struct.unpack('<I', Info[0x38:0x3C])[0] # map name                I_Unk9 = struct.unpack('<I', Info[0x68:0x6C])[0] # map name                #dhexfile(pMemory.read(I_Unk2, 64), 'Info%d_Unk'%j)                                I_Clients, I_Playing = struct.unpack('<II', Info[0x48:0x50])                if I_Unk2 > 0:                    Servers[j]['name'] = pMemory.read_nullterm_unicode(I_Unk2)                Servers[j]['clients'] = I_Clients                Servers[j]['playing'] = I_Playing                if I_Unk3 > 0 and I_Unk4 > 0:                    Servers[j]['email1'] = pMemory.read_nullterm_unicode(I_Unk3)                    Servers[j]['email2'] = pMemory.read_nullterm_unicode(I_Unk4)                if I_Unk5 > 0:                    Servers[j]['wadurl1'] = pMemory.read_nullterm_unicode(I_Unk5)                if I_Unk6 > 0:                    Servers[j]['wadurl2'] = pMemory.read_nullterm_unicode(I_Unk6)                if I_Unk7 > 0:                    Servers[j]['game'] = pMemory.read_nullterm_unicode(I_Unk7)                if I_Unk8 > 0:                    Servers[j]['map'] = pMemory.read_nullterm_unicode(I_Unk8)                if I_Unk9 > 0:                    Servers[j]['gametype'] = pMemory.read_nullterm_unicode(I_Unk9)                        self.servers = Servers        #print('%d servers read.' % (len(self.servers)))                def __del__(self):        self.close()            def close(self):        if self.hProcess is not None:            self.hProcess.terminate()        if self.pMemory is not None:            self.pMemory.close()        self.hProcess = None        self.pMemory = None