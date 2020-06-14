from vkbottle.rule import AbstractMessageRule, ChatActionRule, VBMLRule
from utils import InitParams
from re import compile, I, S

class AddRule:
	from vkbottle.framework.framework.handler.message import COL_RULES

	def __init__(self, name):
		self.name = name

	def __call__(self, cls):
		self.COL_RULES[self.name] = cls
		return cls

@AddRule('audio_message')
class AudioMessage(VBMLRule, InitParams):
	class AM(dict):
		__getattr__ = dict.get

	async def check(self, message):
		if (audio_message := message.attachments and message.attachments[0].audio_message) \
			and (text := self.amessage.get_text(audio_message)): await super().check(self.AM(text = text))

@AddRule('is_admin')
class IsAdmin(AbstractMessageRule, InitParams):
	def __init__(self, adm):
		self.adm = adm

	async def check(self, message):
		if items := (await self.api.messages.get_conversations_by_id(peer_ids = message.peer_id)).items:
			chat_settings = items[0].chat_settings
			is_admin = message.from_id == chat_settings.owner_id or message.from_id in chat_settings.admin_ids
			return self.adm and is_admin or not self.adm and not is_admin

@AddRule('with_text')
class WithText(AbstractMessageRule, InitParams, lvl_class = True):
	def __init__(self, wt):
		self.wt = wt

	async def check(self, message):
		if text := await self.lvl_class.hello_text(): self.context.kwargs = {'text': text}
		return self.wt and text or not self.wt and not text

@AddRule('with_reply_message')
class WithReplyMessage(AbstractMessageRule):
	def __init__(self, wrm):
		self.wrm = wrm
	
	async def check(self, message):
		is_wrm = message.reply_message and message.reply_message.from_id > 0
		return self.wrm and is_wrm or not self.wrm and not is_wrm

@AddRule('from_id_pos')
class FromIdPos(AbstractMessageRule):
	def __init__(self, fip):
		self.fip = fip
	
	async def check(self, message):
		is_fip = message.from_id > 0
		return self.fip and is_fip or not self.fip and not is_fip

@AddRule('regex')
class RegexRule(AbstractMessageRule):
	def __init__(self, regex):
		self.compile = compile(regex, flags = I + S)

	async def check(self, message):
		return bool(self.compile.search(message.text))


AddRule('chat_action_rule')(ChatActionRule)
