from aiohttp.web import Response

def options(*handlers):
	def decorator(coro):
		async def new_coro(request):
			try:
				kwargs = {handler.__name__: await handler(request)
					for handler in handlers}
				if all(kwargs.values()):
					try: return await coro(request, **kwargs)
					except TypeError: return Response(text = 'Error!', status = 500)
			except: return Response(text = 'Error!', status = 400)
		return new_coro
	return decorator