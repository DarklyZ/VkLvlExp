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

	@staticmethod
	async def user_id(request):
		if key := request.headers.getone('key', False):
			return await data.lvl.join_key(key)

	@staticmethod
	async def chat_settings(request):
		if items := (await data.bot.api.messages.get_conversations_by_id(peer_ids=data.lvl.peer_id)).items:
			return items[0].chat_settings

	@staticmethod
	def params(*keys):
		async def params(request):
			obj = await request.json()
			if all(key in obj for key in set(keys)):
				return obj

		return params