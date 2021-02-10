def options(*handlers):
	def decorator(coro):
		async def new_coro(request):
			try:
				kwargs = {handler.__name__: await handler(request)
					for handler in handlers}
				if all(kwargs.values()):
					try: return await coro(request, **kwargs)
					except TypeError: pass
			except: pass
		return new_coro
	return decorator