from aiohttp.web import Response
from utils import Data as data

class Options:
	def __init__(self, *, rules = None, keys = None):
		self.handlers = []
		if keys:
			self.json_keys = keys
			self.handlers.append(type(self).__dict__['body'])
		if rules:
			self.handlers.extend(v for k, v in type(self).__dict__.items() if k in rules)

	def __call__(self, coro):
		async def new_coro(request):
			try:
				kwargs = {handler.__name__: await handler(self, request)
					for handler in self.handlers}
				if all(kwargs.values()):
					try: return await coro(request, **kwargs)
					except TypeError: return Response(text = 'Error!', status = 500)
				else: return Response(text = 'Error!', status = 400)
			except: return Response(text = 'Error!', status = 400)
		return new_coro

	async def body(self, request):
		self.json = await request.json()
		if all(key in self.json for key in self.json_keys):
			return self.json

	async def secret_key(self, request):
		if self.json['secret_key'] == data.bot.callback.secret_key:
			return self.json['secret_key']

	async def user_id(self, request):
		if key := request.headers.getone('key', False):
			return await data.lvl.join_key(key)

	async def chat_settings(self, request):
		if items := (await data.bot.api.messages.get_conversations_by_id(peer_ids = data.lvl.peer_id)).items:
			return items[0].chat_settings