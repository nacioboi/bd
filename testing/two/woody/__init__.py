import datetime
import inspect
import base64
import sys
import os


WOODY_INSTANCE:"Woody" = None



def _debug_print(self, prefix:str, *args, **kwargs):
	str = f"{prefix}"
	for arg in args:
		str += f"{arg} "
	str += "\033[0m"
	print(str, **kwargs)
	if "end" in kwargs:
		str += kwargs["end"]
	self._add_contents_to_log(base64.b64encode(str.encode("utf-8")).decode("utf-8"))



class FilterAttempt:
	"""
	You may use a "FilterAttempt" class to gradually filter out the output of
	the logging system.
	"""
	def __init__(self, name) -> None:
		global WOODY_INSTANCE
		self.contents = WOODY_INSTANCE._decode_log(name)
	
	def _get_time_out_of_line(self, line):
		return line.split("]~[")[0][1:]

	def filter_by_time(self, start_date_time, end_date_time):
		"""
		Filter the log by a start date-time and an end date-time.
		"""
		start_date_time = datetime.datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S")
		end_date_time = datetime.datetime.strptime(end_date_time, "%Y-%m-%d %H:%M:%S")
		lines = []
		for line in self.contents.split("\n"):
			time = self._get_time_out_of_line(line)
			time = datetime.datetime.strptime(time, "%H:%M:%S")
			if time >= start_date_time and time <= end_date_time:
				lines.append(line)
		self.contents = "\n".join(lines)
	
	def _get_class_name_out_of_line(self, line):
		"""
		Extract the class name from a log line.
		"""
		return line.split("]~[")[1]

	def filter_by_class(self, class_name):
		"""
		Filter the log by a class name.
		"""
		lines = []
		for line in self.contents.split("\n"):
			if self._get_class_name_out_of_line(line) == class_name:
				lines.append(line)
		self.contents = "\n".join(lines)



class Woody:
	"""
	You must have one and only one Woody instance to act as a main configuration
	for the library.
	"""
	def __init__(self, log_files_path:str="") -> None:
		global WOODY_INSTANCE
		if WOODY_INSTANCE:
			raise Exception("Woody instance already exists!")
		WOODY_INSTANCE = self
		self.log_files_path = log_files_path
		try:
			os.mkdir(self.log_files_path)
		except FileExistsError:
			pass

	def _decode_log(self, name):
		str = ""
		with open(f"{self.log_files_path}/{name}.log", "r") as f:
			str = f.read()
		lines = []
		for line in str.split("\n"):
			lines.append(base64.b64decode(line).decode("utf-8"))
		str = ""
		for line in lines:
			str = f"{line}\n"
		return str



class ColorConfiguration:
	def __init__(self) -> None:
		self.reset_color = "\033[0m"

	def _make_color(self, *args):
		return f"\033[{';'.join(args)}m"

	def set_normal_color(self, *args):
		self.normal_color = self._make_color(*args)
	
	def set_time_color(self, *args):
		self.time_color = self._make_color(*args)

	def set_class_color(self, *args):
		self.class_color = self._make_color(*args)
	
	def set_caller_color(self, *args):
		self.caller_color = self._make_color(*args)

	def set_message_color(self, *args):
		self.message_color = self._make_color(*args)

	@staticmethod
	def _default() -> "ColorConfiguration":
		configuration = ColorConfiguration()
		configuration.set_normal_color("97")
		configuration.set_time_color("36")
		configuration.set_class_color("33")
		configuration.set_caller_color("1","35")
		configuration.set_message_color("1","31")
		return configuration



class DebugContext:
	"""
	You may specify new separate logging contexts.
	A Logging Context will allow, for example, separating the logging output
	of two different threads.
	This will allow easier understanding of the logs.
	"""

	def __init__(self, name:str, do_save_logs=False, do_use_time=False,
			colors:"ColorConfiguration"=ColorConfiguration._default(),
			time_format:str="%H:%M:S") -> None:
		self.name = name
		self.do_save_logs = do_save_logs
		self.do_use_time = do_use_time
		self.colors = colors
		self.time_format = time_format
		self.class_name = None
		self.color_on_flag = True

	def set_color_on(self):
		self.color_on_flag = True
	
	def set_color_off(self):
		self.color_on_flag = False
	
	def set_class_name(self, class_name):
		self.class_name = class_name

	def _add_contents_to_log(self, message):
		if not self.do_save_logs:
			return
		with open(f"{WOODY_INSTANCE.log_files_path}/{self.name}.log", "a") as f:
			f.write(f"{message}\n")

	def __get_caller_function(self, position):
		return inspect.stack()[position+2][3]

	def _get_colored_time(self) -> str:
		if not self.do_use_time:
			return ""
		color = ""
		if self.color_on_flag:
			color = self.colors.time_color
		if len(self.time_format) != 0:
			return f"{color}{datetime.datetime.now().strftime(self.time_format)}{self.colors.reset_color}"
		else:
			return f"{color}{datetime.datetime.now()}{self.colors.reset_color}"

	def _get_colored_class_name(self) -> str:
		color = ""
		if self.color_on_flag:
			color = self.colors.class_color
		return f"{color}{self.class_name}{self.colors.reset_color}"

	def _get_colored_caller_function(self) -> str:
		color = ""
		if self.color_on_flag:
			color = self.colors.caller_color
		return f"{color}{self.__get_caller_function(1)}{self.colors.reset_color}"

	def get_time(self):
		return self._get_colored_time()

	def get_class_name(self):
		return self._get_colored_class_name()

	def get_caller_function(self, position):
		return self._get_colored_caller_function(position)

	def log_line(self, *args, **kwargs):
		normal_color = ""
		message_color = ""
		if self.color_on_flag:
			normal_color = self.colors.normal_color
			message_color = self.colors.message_color

		msg = ""
		msg += f"{normal_color}[{self.colors.reset_color}"
		msg += self._get_colored_time()
		msg += f"{normal_color}]~[{self.colors.reset_color}"
		msg += self._get_colored_class_name()
		msg += f"{normal_color}.{self.colors.reset_color}"
		msg += self._get_colored_caller_function()
		msg += f"{normal_color}]>>>{message_color}"

		_debug_print(self, msg, *args, **kwargs)

	def get_reset_poison(self):
		return "\033[1m~\033[0m"

	def __sequence_occurs_after(self, sequence, string, index):
		try:
			for i, char in enumerate(sequence):
				if string[index+i] != char:
					return False
			return True
		except IndexError:
			return False

	def simple_log_line(self, *args, **kwargs):
		msg = ""
		for arg in args:
			msg += f"{arg} "
		
		def filter(msg, start_index):
			_msg = msg
			_sequence1 = self.get_reset_poison()
			_sequence2 = "\033[0m"
			for i in range(start_index, len(_msg)):
				if self.__sequence_occurs_after(_sequence1, _msg, i):
					_msg = _msg[:i] + "\033[0m" + _msg[i+len(_sequence1):]
					return _msg, i
				if self.__sequence_occurs_after(_sequence2, _msg, i):
					_msg = _msg[:i] + self.colors.normal_color + _msg[i+len(_sequence2):]
					return _msg, i
			
			return None, None
		
		index = 0
		while True:
			_msg = None
			_msg, index = filter(msg, index)
			if _msg == None:
				break
			msg = _msg
			index = index + 1
		
		_debug_print(self, self.colors.normal_color, msg, **kwargs)


	def simple_log(self, *args, **kwargs):
		if not "end" in kwargs:
			kwargs["end"] = ""
		_debug_print(self, "", *args, **kwargs)
	

if __name__ == "__main__":
	Woody(f"{os.getcwd()}/logs")

	DEBUG_CONTEXT = DebugContext(
		"debug", 
		do_save_logs=True,
		do_use_time=True,
		colors=ColorConfiguration._default(),
		time_format=""
	)
      # DEBUG_CONTEXT.set_format("[%{ time_here }%]~[%{ class_name_here }%.%{ caller_function_here }%]>>>%{ message_here }%")
	DEBUG_CONTEXT.simple_log_line(f"[{DEBUG_CONTEXT.get_time()}]~>>>{DEBUG_CONTEXT.get_reset_poison()}Started a new!")
      # DEBUG_CONTEXT.simple_log_line("[%{ get_time() }%]~>>>%{ no_normal }%Started a new!")
	DEBUG_CONTEXT.log_line("Hello there!")