from vkbottle.framework.labeler.base import DEFAULT_CUSTOM_RULES
from datetime import datetime, tzinfo, timedelta
from aiohttp import ClientSession
from vbml import Patcher

class Data:
	def __init_subclass__(cls, run = False):
		for k, v in cls.__annotations__.items():
			if v is Data: setattr(Data, k, getattr(cls, k))
		if run:
			cls().__run__()

class API:
	def __init__(self):
		self.session = ClientSession()

	def __del__(self):
		if not self.session.closed:
			self.session.close()

class SetRule:
	custom_rules = DEFAULT_CUSTOM_RULES.copy()

	def __init__(self, name):
		self.name = name

	def __call__(self, cls):
		self.custom_rules[self.name] = cls
		return cls

class MyPatcher(Patcher):
	def __init__(self):
		super().__init__()
		self.set_validators()

	def set_validators(self):
		@self.validator(key = 'int')
		def int_validator(value):
			return int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None
		@self.validator(key = 'pos')
		def pos_validator(value):
			return int(value) if value.isdigit() or value[:1] == '+' and value[1:].isdigit() else None
		@self.validator(key = 'max')
		def max_validator(value, extra):
			return value if len(value) <= int(extra) else None
		@self.validator(key = 'inc')
		def inc_validator(value, *extra):
			return value.lower() if value.lower() in extra else None

class DateBase:
	class tz(tzinfo):
		utcoffset = lambda self, dt: timedelta(hours = 5)
		dst = lambda self, dt: timedelta()
		tzname = lambda self, dt: '+05:00'

	def __init_subclass__(cls):
		cls.tz = DateBase.tz()

	@property
	def now(self):
		return datetime.now(self.tz)

def getcake(bdate, now):
	if isinstance(bdate, str):
		bdate = datetime.strptime(bdate, '%d.%m' if bdate.count('.') == 1 else '%d.%m.%Y')
		return '🎂' if bdate.day == now.day and bdate.month == now.month else ''
	return ''

def getprice(slcount, lvl):
	if slcount == 0: return 120
	elif (price := round((1.1 ** slcount - 1) * 1e4)) < (maxexp := lvl * 2000 - 50):
		return price
	return maxexp

def getpercent(slcounts):
	return percent if (percent := 5 * slcounts + 5) < 50 else 50
