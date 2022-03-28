from asyncio import iscoroutinefunction
from utils import Data as data

class Rules(list):
	def __init__(self, **kwargs):
		super().__init__()
		self.post_fs = []
		self.kwargs = kwargs
		for rule in kwargs:
			self.append(getattr(self, rule))

	async def post(self):
		for func in self.post_fs:
			if iscoroutinefunction(func):
				await func()
			else: func()
		self.post_fs.clear()

	async def body(self, request):
		self.json = await request.json()
		if all(key in self.json for key in self.kwargs['body']):
			return self.json

	async def secret_key(self, request):
		if self.json['secret'] == data.bot.callback.secret_key:
			return self.json['secret']

	async def user_id(self, request):
		self.post_fs.append(lambda: data.lvl.clear())
		if key := request.headers.getone('key', False):
			return await data.lvl.join_key(key)

	async def chat_settings(self, request):
		if items := (await data.bot.api.messages.get_conversations_by_id(peer_ids = data.lvl.peer_id)).items:
			return items[0].chat_settings