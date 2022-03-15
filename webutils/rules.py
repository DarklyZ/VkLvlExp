from utils import Data as data

class Rules(list):
	def __init__(self, rules, keys):
		super().__init__()
		if keys:
			self.append(type(self).__dict__['body'])
		for rule in rules:
			self.append(type(self).__dict__[rule])
		self.keys = keys

	async def body(self, request):
		self.json = await request.json()
		if all(key in self.json for key in self.keys):
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