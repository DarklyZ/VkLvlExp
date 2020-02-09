from vkbottle.rule import AbstractMessageRule, ChatActionRule

class add_rule:
	from vkbottle.handler.handler import COL_RULES

	def __init__(self, name):
		self.name = name

	def __call__(self, func):
		self.COL_RULES[self.name] = func
		return func

@add_rule('is_admin')
class IsAdmin(AbstractMessageRule):
	from vkbottle.api import Api as api

	def __init__(self, adm):
		self.adm = adm
		self.api = self.api.get_current()

	async def check(self, message):
		items = (await self.api.messages.getConversationsById(peer_ids = message.peer_id))['items']
		if not items: return False
		chat_settings = items[0]['chat_settings']
		is_admin = message.from_id == chat_settings['owner_id'] or message.from_id in chat_settings['admin_ids']
		return self.adm and is_admin or not self.adm and not is_admin

@add_rule('with_text')
class WithText(AbstractMessageRule):
	from lvls import LVL as lvl_class

	def __init__(self, wt):
		self.wt = wt
		self.lvl_class = self.lvl_class.get_current()

	async def check(self, message):
		text = await self.lvl_class.hello_text()
		if self.wt and text:
			self.context.kwargs = {'text': text}
			return True
		return not self.wt and not text

@add_rule('with_reply_message')
class WithReplyMessage(AbstractMessageRule):
	def __init__(self, wrm):
		self.wrm = wrm
	
	async def check(self, message):
		is_wrm = message.reply_message and message.reply_message.from_id > 0
		return self.wrm and is_wrm or not self.wrm and not is_wrm

@add_rule('from_id_pos')
class FromIdPos(AbstractMessageRule):
	def __init__(self, fip):
		self.fip = fip
	
	async def check(self, message):
		is_fip = message.from_id > 0
		return self.fip and is_fip or not self.fip and not is_fip

add_rule('chat_action_rule')(ChatActionRule)