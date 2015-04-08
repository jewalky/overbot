import struct;

class ByteStream:
	def __init__(self):
		self.reset();
		
	def reset(self):
		self.buffer = bytearray(0);
		self.position_read = 0;
		self.position_write = 0;
		
	def load_from_file(self, filename):
		try:
			f = open(filename, 'rb');
			self.buffer = bytearray(0);
			while True:
				str = f.read(1024);
				self.buffer[len(self.buffer):len(self.buffer)] = str;
				if len(str) != 1024:
					break;
			f.close();
		except IOError:
			return False;
		return True;
		
	def save_to_file(self, filename):
		try:
			f = open(filename, 'wb');
			wpos = 0;
			while wpos < len(self.buffer):
				f.write(self.buffer[wpos:wpos+1024]);
				wpos += 1024;
			f.close();
		except IOError:
			return False;
		return True;
		
	def seek(self, pos):
		if pos < 0:
			pos = 0;
		if pos > len(self.buffer):
			pos = len(self.buffer);
		self.position_read = pos;
		self.position_write = pos;
		
	def read(self, size):
		if self.position_read+size > len(self.buffer):
			size = len(self.buffer)-self.position_read;
		if size <= 0:
			return bytearray(0);
		buf = self.buffer[self.position_read:self.position_read+size];
		self.position_read += size;
		return buf;
		
	def write(self, buf):
		self.buffer[self.position_write:self.position_write] = buf;
		self.position_write += len(buf);
		
	def read_int8(self):
		buf = self.read(1);
		if not buf:
			return 0;
		try:
			return struct.unpack('<b', buf)[0];
		except:
			return 0;
		
	def read_uint8(self):
		buf = self.read(1);
		if not buf:
			return 0;
		try:
			return struct.unpack('<B', buf)[0];
		except:
			return 0;
	
	def read_int16(self):
		buf = self.read(2);
		if len(buf) != 2:
			return 0;
		try:
			return struct.unpack('<h', buf)[0];
		except:
			return 0;
		
	def read_uint16(self):
		buf = self.read(2);
		if len(buf) != 2:
			return 0;
		try:
			return struct.unpack('<H', buf)[0];
		except:
			return 0;
		
	def read_int32(self):
		buf = self.read(4);
		if len(buf) != 4:
			return 0;
		try:
			return struct.unpack('<l', buf)[0];
		except:
			return 0;
		
	def read_uint32(self):
		buf = self.read(4);
		if len(buf) != 4:
			return 0;
		try:
			return struct.unpack('<L', buf)[0];
		except:
			return 0;
		
	def read_int64(self):
		buf = self.read(8);
		if len(buf) != 8:
			return 0;
		try:
			return struct.unpack('<q', buf)[0];
		except:
			return 0;
		
	def read_uint64(self):
		buf = self.read(8);
		if len(buf) != 8:
			return 0;
		try:
			return struct.unpack('<Q', buf)[0];
		except:
			return 0;
		
	def write_int8(self, int8):
		self.write(struct.pack('<b', int8&0xFF));
		
	def write_uint8(self, uint8):
		self.write(struct.pack('<B', uint8&0xFF));
		
	def write_int16(self, int16):
		self.write(struct.pack('<h', int16&0xFFFF));
	
	def write_uint16(self, uint16):
		self.write(struct.pack('<H', uint16&0xFFFF));
		
	def write_int32(self, int32):
		self.write(struct.pack('<l', int32&0xFFFFFFFF));
		
	def write_uint32(self, uint32):
		self.write(struct.pack('<L', uint32&0xFFFFFFFF));
		
	def write_int64(self, int64):
		self.write(struct.pack('<q', int64&0xFFFFFFFFFFFFFFFF));
		
	def write_uint64(self, uint64):
		self.write(struct.pack('<Q', uint64&0xFFFFFFFFFFFFFFFF));
		
	def read_fixed_string(self, size):
		_str = bytearray(size);
		for i in range(size):
			_str[i] = self.read_uint8();
		return _str.decode('utf-8');
		
	def write_fixed_string(self, string, size):
		string = string.encode('utf-8');
		_str = bytearray(size);
		for i in range(size):
			_str[i] = string[i];
		self.write(_str);
	
	def read_string(self):
		_str = bytearray();
		while True:
			c = self.read_uint8();
			if c == 0:
				break;
			_str.append(c);
		return _str.decode('utf-8');
	
	def write_string(self, string):
		string = string.encode('utf-8');
		for c in string:
			self.write_uint8(c);
		self.write_uint8(0);