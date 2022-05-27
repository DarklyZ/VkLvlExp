from utils import Data
from aiohttp.web import Response

class Custom(Data):
	class Rule(Data):
		def __init_subclass__(cls, name):
			setattr(Custom.Rules, name, cls)

		def __init__(self, value):
			self.value = value

	class Rules(dict):
		def __init__(self, **kwargs):
			super().__init__(
				(key, getattr(self, key)(value).check) for key, value in kwargs.items()
			)

		def __call__(self, coro):
			return Custom(self, coro).coro

	def __init__(self, rules, base):
		self.rules = rules
		self.base = base

	def __call__(self, request):
		self.request = request
		return self

	async def __aenter__(self):
		return {key: await value(self.request) for key, value in self.rules.items()}

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if 'user_id' in self.rules: self.lvl(None)

	async def coro(self, request):
		async with self(request) as kwargs:
			if all(kwargs.values()):
				try: return await self.base(request, **kwargs)
				except TypeError: return Response(text = 'TypeError', status = 500)
			else: print(kwargs)
