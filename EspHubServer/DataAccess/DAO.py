from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, Text, BLOB
from sqlalchemy.orm import relationship
from DataAccess.DAC import Base
from DataAccess.CustomTypes import CustomJson
from datetime import datetime
from Tools.Log import Log
import json

log = Log.get_logger()


class Device(Base):
	"""
	Table represent single device
	:param id: Device unique ID (for ESP module is internal manufacturer id, for UniLib is UUID).
	:type id: str
	:param name: Recognizable device name.
	:type name: str
	:param status: Device status: 'validated' when user validate device, 'waiting' waiting for validation
	:type status: str
	:param provided_func: List of provided function. Store original value from client device, so this parameter has purpose only before validation.
		After validation provided functions in rich format are stored in Ability Table - list of strings (json serializable).
	:type provided_func: list
	"""
	__tablename__ = 'device'
	VALIDATED = 'validated'
	WAITING = 'waiting'

	# columns
	id = Column('id', String(64), primary_key=True, unique=True)
	name = Column('name', String(64), nullable=False)
	status = Column('status', String(16), default='validated')
	provided_func = Column('provided_func', CustomJson, nullable=False, default=list())

	# forward dependencies
	abilities = relationship('Ability', back_populates='device')
	records = relationship('Record', back_populates='device')
	telemetries = relationship('Telemetry', back_populates='device')
	displays = relationship('Display', back_populates='device')

	def __repr__(self):
		return 'Device: <{}>'.format((self.id, self.name))

	def serialize(self):
		object_dic = self.__dict__.copy()
		object_dic.pop('_sa_instance_state', None)  # remove SQLAlchemy internal info
		return object_dic

	def to_json(self):
		"""
		Serialize object into JSON.
		:return: String in JSON format.
		"""
		return json.dumps(self.serialize())


class Ability(Base):
	"""
	Table represent one of device abilities
	:param id: Unique record ID - automatically generated.
	:type id: int
	:param name: Ability name (e.g. 'temp', 'hum') - mandatory.
	:type name: str
	:param user_name: Human readable name (e.g. 'Temperature', 'Humidity in room') - optional.
	:type user_name: str
	:param io: Is it 'out' or 'in' device - optional.
	:type str
	:param category: Ability category (e.g. 'sensor', 'button', 'display', 'switch') - optional.
	:type category: str
	:param unit: Ability unit - optional.
	:type unit: str
	:param default_value: Default value for sensors - optional.
	:type default_value: str
	:param data_type: Indicate type of provided data (e.g. 'str', 'int', 'float', 'json') - default 'str'.
	:type data_type: str
	:param description: Description - optional.
	:type description: str
	:param device: Owner device.
	:type device: Device
	"""
	__tablename__ = 'ability'
	IN = 'in'
	OUT = 'out'
	CATEGORY_SENSOR = 'sensor'
	CATEGORY_SWITCH = 'switch'
	CATEGORY_BUTTON = 'button'
	CATEGORY_DISPLAY = 'display'
	TYPE_INT = 'int'
	TYPE_FLOAT = 'float'
	TYPE_STR = 'str'
	TYPE_JSON = 'json'

	# columns
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(256), nullable=False)
	user_name = Column('userName', String(256), nullable=True)
	io = Column('io', String(16), nullable=True)
	category = Column('category', String(32), nullable=True)
	unit = Column('unit', String(16), nullable=True)
	default_value = Column('defaultValue', String(16), nullable=True)
	data_type = Column('dataType', String(16), default='str')
	description = Column('description', String(512), nullable=True)

	# downward dependencies
	device_id = Column('device_id', String(64), ForeignKey('device.id'))
	device = relationship(Device, cascade='delete', back_populates='abilities')

	# forward dependencies
	displays_ng = relationship('DisplayNg', back_populates='ability')

	def __repr__(self):
		return 'Ability: <{}>'.format((self.id, self.name, self.user_name, self.io, self.category, self.device_id))

	def init_with_json(self, json_str):
		"""
		Initialize object from string in JSON format.
		:param json_str: String in JSON format.
		"""
		try:
			obj = json.loads(json_str)
		except json.JSONDecodeError:
			raise ValueError("DAO class Ability cannot load invalid JSON.")

		self.name = obj.get('name')
		self.user_name = obj.get('user_name')
		self.io = obj.get('io')
		self.category = obj.get('category')
		self.unit = obj.get('unit')
		self.default_value = obj.get('default_value')
		self.data_type = obj.get('data_type')
		self.description = obj.get('desc')

	def serialize(self):
		"""
		Serialize object into dictionary.
		:return: Object representation as dictionary.
		"""
		object_dic = self.__dict__.copy()
		object_dic.pop('_sa_instance_state', None)  # remove SQLAlchemy internal info
		object_dic.pop('device', None)  # remove non-serializable Device reference
		return object_dic

	def to_json(self):
		"""
		Serialize object into JSON.
		:return: String in JSON format.
		"""
		return json.dumps(self.serialize())


class Record(Base):
	"""
	Table represent one of Device records - hold data from devices.
	:param id: Unique record ID - automatically generated.
	:type id: int
	:param time: Time of creation - default is current time.
	:type time: datetime
	:param type: Type of ability.
	:type type: str
	:param value: Value from device.
	:type value: str
	:param device_id: ID of device, which is owner of record.
	:type device_id: str
	:param device: Owner device.
	:type device: Device
	"""
	__tablename__ = 'record'
	SUM_NONE = 'none'
	SUM_MINUTELY = 'T'
	SUM_HOURLY = 'H'
	SUM_DAILY = 'D'
	SUM_WEEKLY = 'W'
	SUM_MONTHLY = 'M'

	id = Column('id', Integer, primary_key=True)
	time = Column('time', DateTime, default=datetime.now())
	name = Column('type', String(64))
	value = Column('value', String(256))
	summarized = Column('summarized', String(16), default=SUM_NONE)

	device_id = Column('device_id', String(64), ForeignKey('device.id'))
	device = relationship(Device, back_populates='records')

	def __repr__(self):
		return 'Record: <{}>'.format((self.id, self.time, self.name, self.value, self.device_id))

	def serialize(self):
		"""
		Serialize object into dictionary.
		:return: Object representation as dictionary.
		"""
		object_dic = self.__dict__.copy()
		object_dic.pop('_sa_instance_state', None)
		object_dic.pop('device', None)
		object_dic['time'] = str(self.time)
		return object_dic


class Telemetry(Base):
	"""
	Table represent incoming telemetry from device.
	:param id: Unique record ID - automatically generated.
	:type id: int
	:param time: Time of creation - default is current time.
	:type time: datetime
	:param rssi: Signal RSSI for ESP device.
	:type rssi: str
	:param heap: Allocated space on heap for ESP device.
	:type heap: str
	:param cycles: Cycles from start for ESP device.
	:type rssi: str
	:param voltage: Voltage on ESP device.
	:type rssi: str
	:param ip: IP address of device.
	:type rssi: str
	:param mac: MAC address of device.
	:type rssi: str
	:param ssid: Wifi network SSID of ESP device.
	:type rssi: str
	:param hostname: Hostname of unilib device.
	"""
	__tablename__ = 'telemetry'

	id = Column('id', Integer, primary_key=True)
	time = Column('time', DateTime, default=datetime.now())
	rssi = Column('rssi', String(8), nullable=True)
	heap = Column('heap', String(32), nullable=True)
	cycles = Column('cycles', String(32), nullable=True)
	voltage = Column('voltage', String(16), nullable=True)
	ip = Column('ip', String(16), nullable=True)
	mac = Column('mac', String(24), nullable=True)
	ssid = Column('ssid', String(128), nullable=True)
	hostname = Column('hostname', String(128), nullable=True)

	device_id = Column('device_id', String(64), ForeignKey('device.id'))
	device = relationship(Device, back_populates='telemetries')

	def __repr__(self):
		return 'Telemetry <{}>'.format((self.id, self.time, self.device_id, self.ssid, self.ip, self.mac))

	def serialize(self):
		"""
		Serialize object into dictionary.
		:return: Object representation as dictionary.
		"""
		object_dic = self.__dict__.copy()
		object_dic.pop('_sa_instance_state', None)
		object_dic.pop('device', None)
		object_dic['time'] = str(self.time)
		return object_dic

	def to_json(self):
		"""
		Serialize object into JSON.
		:return: String in JSON format.
		"""
		return json.dumps(self.serialize())


class Display(Base):
	"""
	Table represent Display connected to Device
	:param id: Unique record ID - automatically generated.
	:type id: int
	:param display_name: Name of specific display device connected to Device.
	:type display_name: str
	:param screen_name: Name of individual screens of display (each display can have more screens).
	:type screen_name: str
	:param params: Additional parameters for display sych as display setting and screen config - JSON serializable object.
	:type params: json
	:param device: Owner device.
	:type device: Device
	"""
	__tablename__ = 'display'

	id = Column('id', Integer, primary_key=True)
	display_name = Column('displayName', String(256), nullable=False)
	screen_name = Column('screenName', String(256), nullable=True)
	params = Column('params', CustomJson, nullable=True)

	device_id = Column('device_id', String(64), ForeignKey('device.id'))
	device = relationship(Device, cascade='delete', back_populates='displays')

	def __repr__(self):
		return "Display <{}>".format((self.id, self.display_name, self.screen_name))


class DisplayNg(Base):
	"""
	New generation of table Display which represent connected display device.
	This table is compatible with new model: ABILITY -> DISPLAYS -> SCREENS
	:param id: Unique display ID - automatically generated.
	:type id: int
	:param name: Name of connected display (for user purpose).
	:type name: String
	:param width: Width of display in pixels.
	:type width: int
	:param height: Height of display in pixels.
	:type height: int
	:param model: Model of connected devices e.g.: SSD1306, ILI9341, ... (mapped in constants).
	:type model: String
	:param params: Additional parameters in JSON.
	:type params: json
	:param ability: Output ability corresponding with this display.
	:type ability: Ability
	:param screens: List of Screens belonging to this display
	:type screens: list
	"""
	MODEL_SSD1306 = 'SSD1306'
	MODEL_ILI9341 = 'ILI9341'

	__tablename__ = 'displayNg'

	# columns
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(64), nullable=False)
	width = Column('width', Integer, nullable=False)
	height = Column('height', Integer, nullable=False)
	model = Column('model', String(32), nullable=False)
	params = Column('params', CustomJson, nullable=True)

	# downward dependencies
	ability_id = Column('ability_id', Integer, ForeignKey('ability.id'))
	ability = relationship(Ability, cascade='delete', back_populates='displays_ng')

	# forward dependencies
	screens = relationship('Screen', back_populates='display_ng')

	def __repr__(self):
		return "DisplayNg <{}>".format((self.id, self.name, self.height, self.width, self.model))


class Screen(Base):
	"""
	Represent single display screen (each display could have N screens).
	Screen content is represent by 'content' column or by 'params' column depend on content_type.
	Content type 'html' store in 'content' column HTML/JS/CSS code which are processed and rendered on display.
	:param id: Unique screen ID - automatically generated.
	:type id: int
	:param name: Name of screen for user purposes.
	:type name: String
	:param description: Description of screen content for user purposes.
	:type description: String
	:param order: Order number of screen. Default is 0. Same value can be used multiple times, but then order cannot be granted.
	:type order: int
	:param rotation_period: Number of second to rewind on the next screen.
	:type rotation_period: int
	:param params: Additional arguments in JSON format.
	:type params: json
	:param content_type: Define type of screen content. By default content is HTML/CSS/JS stored in column 'content'.
	:type content_type: String
	:param content: Raw content in various format, primary HTML/CSS/JS.
	:type content: BLOB
	:param display_ng: Parent display
	:type display_ng: DisplayNg
	"""
	CONTENT_TYPE_HTML = 'html'

	__tablename__ = 'screen'

	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(64), nullable=False)
	description = Column('description', String(512), nullable=True)
	order = Column('order', Integer, default=0)
	rotation_period = Column('rotationPeriod', Integer, default=0)
	params = Column('params', CustomJson, nullable=True)
	content_type = Column('contentType', String(32), default=CONTENT_TYPE_HTML)
	content = Column('content', BLOB, nullable=True)

	display_ng_id = Column('display_ng_id', Integer, ForeignKey('displayNg.id'))
	display_ng = relationship(DisplayNg, cascade='delete', back_populates='screens')

	def __repr__(self):
		return "Screen <{}>".format((self.id, self.name, self.order, self.rotation_period, self.content_type))