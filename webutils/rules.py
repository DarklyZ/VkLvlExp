from utils import Data

class Rules(list, Data):
	def __init__(self, **kwargs):
		super().__init__()
		self.kwargs = kwargs
		for rule in kwargs:
			self.append(getattr(self, rule))

	async def body(self, request):
		self.json = await request.json()
		if all(key in self.json for key in self.kwargs['body']):
			return self.json

	async def secret_key(self, request):
		if self.json['secret'] == self.bot.callback.secret_key:
			return self.json['secret']

	async def user_id(self, request):
		if key := request.headers.getone('key', False):
			return await self.lvl.join_key(key)

	async def chat_settings(self, request):
		if items := (await self.bot.api.messages.get_conversations_by_id(peer_ids = self.lvl.peer_id)).items:
			return items[0].chat_settings