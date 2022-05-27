from .base import Custom

class Body(Custom.Rule, name = 'body'):
	async def check(self, request):
		json = await request.json()
		if all(key in json for key in self.value):
			return json

class SecretKey(Custom.Rule, name = 'secret_key'):
	async def check(self, request):
		json = await request.json()
		if json['secret'] == self.bot.callback.secret_key:
			return json['secret']

class UserId(Custom.Rule, name = 'user_id'):
	async def check(self, request):
		if key := request.headers.getone('key', False):
			return await self.lvl.join_key(key)

class ChatSettings(Custom.Rule, name = 'chat_settings'):
	async def check(self, request):
		if items := (await self.bot.api.messages.get_conversations_by_id(peer_ids=self.lvl.peer_id)).items:
			return items[0].chat_settings