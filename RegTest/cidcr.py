# -*- coding:gbk -*-

import sys
import socket
import select
import time
import json

reload(sys)

IDCR_CURRENT_VERSION = "1.0"

IDCR_RESULT_OK = 1
IDCR_RESULT_ERR = 0

IDCR_DB_WORKER_ID = 1
IDCR_FILE_WORKER_ID = 2

LAN_MARK = 0
WAN_MARK = 1

FILE_START = 0
FILE_TRAN = 1
FILE_END = 2
FILE_START_END = 3
FILE_CHUNK_LEN = 4096

class idcr:
	def __init__(self, db_id, host, port):
		self._host = host
		self._port = port
		self._id = db_id

		self._fd = None
		self._buffer = ""
		self._records = ""
		self._max_packet_header = 100
		
		self._last_result = -1
		self._error_info = ""
		
		self._timeout_value = 0
	
	def __del__(self):
		if self._fd:
			try:
				self._fd.close()
				self._fd = None
			except Exception, e:
				print str(e)
	
	def connect(self):
		# connect
		try:
			self._fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if self._timeout_value > 0:
				self._fd.settimeout(self._timeout_value)
			
			self._fd.connect((self._host, self._port))
		except socket.error, msg:
			self._error_info = "connect failed: %s" % msg
			
			self._fd.close()
			self._fd = None	
	
	def disconnect(self):
		if self._fd:
			try:
				self._fd.close()
			except:
				pass
		
		self._fd = None
	
	def reconnect(self):
		self.disconnect()
		self.connect()
	
	def set_timeout(self, timeout):
		self._timeout_value = timeout

	def unset_timeout(self):
		self._timeout_value = 0

	def clear_buffer(self):
		self._buffer = ""

	def get_buffer(self):
		return self._buffer

	# 1 for complete packet; 0 for imcomplete; -1 for invalid response
	def check_response_complete(self):
		if len(self._buffer) <= 0:
			return 0

		p = self._buffer.find("\r\n")
		if p == -1:
			if len(self._buffer) >= self._max_packet_header:
				return -1
			return 0

		# check system error return
		if (p + 2) == len(self._buffer):
			self._last_result = False
			self._error_info = self._buffer[0:p]  
			self._buffer = ""

			return 1
		
		#version worker_id result bytes\r\ndata\r\n
		packets = self._buffer.split("\r\n")
		packet_headers = packets[0].split(" ")

		if len(packet_headers) < 4:
			self._last_result = False
			self._error_info = "invalid packet headers:%s" % packets[0]
			return -1
		
		if int(packet_headers[2]) == IDCR_RESULT_OK:
			self._last_result = True
		else:
			self._last_result = False
		bytes_block = int(packet_headers[3])
		
		if len(self._buffer) >= len(packet_headers) + 2 + bytes_block + 2:
			if len(packets) > 1:
				#self._records = packets[1]
				header_len = (len(packets[0]))
				self._records = self._buffer[ (header_len + 2) : (header_len + 2 + bytes_block)]
				self._buffer = self._buffer[(header_len + 2 + bytes_block + 2):]
			return 1
		else:
			return 0
	
	def send_packet(self, packet):
		if not self._fd:
			self.connect()
		
		return self._fd.send(packet)
	
	# True for good, False for error, including timeout
	def read_response(self):
		start = time.time()
		while True:
			# blocking read
			data = self._fd.recv(4096)
				
			if len(data) > 0:
				self._buffer += data
			else:
				self._fd.setblocking(0)
				
				now = time.time()
				remain = self._timeout_value - (now - start)
				
				if remain <= 0:
					self._timeout = True
					return False
				
				rfds = [self._fd]
				readfds, _writefds, _errorfds = select.select(rfds, [], [], remain)
				if len(readfds) > 0:
					data = self._fd.recv(4096)
					
					if len(data) > 0:
						self._buffer += data
					else:
						return False
				return False
			
			# check if we got a complete packet
			# 1 for complete packet; 0 for imcomplete; -1 for invalid response
			retval = self.check_response_complete()
			if retval == 1:
				return self._last_result
			elif retval == 0:
				continue
			else:
				return False

	def get_result(self):
		if self._last_result == -1:
			return "no result from idcr"
		
		return self._records
	
	def get_last_error(self):
		return self.get_result()
			

class idcr_db_proxy(idcr):
	def __init__(self, db_id, host = '183.60.62.43', port = 6380):
		idcr.__init__(self, IDCR_DB_WORKER_ID, host, port)
		self._db_id = db_id
		self._process_info = []
		
	def reset_process_info(self):
		self._process_info = []
	
	def add_process_info(self, info):
		self._process_info.append("[%s] %s" % (time.strftime("%Y%m%d %H:%M:%S"), info))
		
	def get_process_info(self):
		return "\n".join(self._process_info)

	def set_db_id(self, db_id):
		self._db_id = db_id
	
	def get_db_id(self):
		return self._db_id
		
	# request: "1.0 1 1 2 %d\r\n%s\r\n" % (len(sql), sql)
	# request: "version type db_id timeout bytes\r\nsql\r\n"
	def markup_request_packet(self, sql, timeout):
		return "%s %d %d %d %d\r\n%s\r\n" % (IDCR_CURRENT_VERSION, self._id, self._db_id, int(timeout), len(sql), sql)
	
	# True for run sql ok, call get_result() to fetch your records if 'select'
	# False for failed, call get_last_error() to fetch reason to failure
	# set timeout in case of blocking long time
	def query(self, sql, timeout = 0):
		if not sql:
			return False
	
		self.reset_process_info()
		retry = 3
		while retry > 0:
			self.clear_buffer()
			self.set_timeout(timeout)
			
			try:
				packet = self.markup_request_packet(sql, timeout)
				retval = self.send_packet(packet)
				self.add_process_info("packet sent(%d bytes), total len:%d bytes" % (retval, len(packet)))
				
			except BaseException, msg:
				self.add_process_info("exception during send_packet():%s" % msg)
				if retry > 0:
					retry -= 1
					self.reconnect()
					
					self.add_process_info("#%d) retry to send packet" % retry)
					time.sleep(0.1)
					
					continue
				else:
					self._error_info = "send_packe() exception: %s" % msg
					return False
			try:
				result = self.read_response()
				if True == result:
					self.add_process_info("read_response() read a complete reply")
				else:
					self.add_process_info("read_response() failed")
					
				return result
			except BaseException, msg:
				if retry > 0:
					retry -= 1
					self.reconnect()
					
					self.add_process_info("#%d) retry to send packet" % retry)
					time.sleep(0.1)
				else:
					self._error_info = "read_response() exception: %s" % msg
					return False			
	
	# set encoding to your encode, if the result is not encoded in UTF8
	# for example, records that consist of chinese should use 'gbk' encoding
	def get_all_list(self, encoding = "gbk"):
		records = self.get_result()
		try:
			data = json.loads(records, encoding)
		except BaseException, msg:
			self.add_process_info("json.loads() exception:%s" % msg)
			return None
		return data

	def get_last_error(self):
		# process info
		# error info
		# system info
		return "process info:\n%s\n--\nerror info:\n%s\n--\nsystem info:\n%s\n" % (self.get_process_info(), self._error_info, idcr.get_last_error(self))

DB_ID = 143
HOST = "183.60.62.43"
PORT = 6380
db_proxy = idcr_db_proxy(DB_ID, HOST, PORT)


if __name__ == "__main__":
	if db_proxy.query("select * from t05_alarm_raw", 1):
		print db_proxy.get_result()
		pass
	else:
		print db_proxy.get_last_error()
		print "database query fail"
