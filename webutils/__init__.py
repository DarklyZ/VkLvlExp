from aiohttp.web import Response
from .rules import Rules

class Options:
	def __init__(self, *, rules = set(), keys = set()):
		self.rules = Rules(rules, keys)

	def __call__(self, coro):
		async def new_coro(request):
			try:
				print(kwargs, self.rules)
				kwargs = {handler.__name__: await handler(self.rules, request)
					for handler in self.rules}
				if all(kwargs.values()):
					try: return await coro(request, **kwargs)
					except TypeError: return Response(text = 'Error!', status = 500)
				else: return Response(text = 'Error!', status = 400)
			except: return Response(text = 'Error!', status = 400)
		return new_coro