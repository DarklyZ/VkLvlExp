from aiohttp.web import Response

class Options:
	def __init__(self, *handlers):
		self.handlers = handlers

	def __call__(self, coro):
		async def new_coro(request):
			try:
				kwargs = {handler.__name__: await handler(request)
					for handler in self.handlers}
				if all(kwargs.values()):
					try: return await coro(request, **kwargs)
					except TypeError: return Response(text = 'Error!', status = 500)
				else: return Response(text = 'Error!', status = 400)
			except: return Response(text = 'Error!', status = 400)
		return new_coro