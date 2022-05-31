from vkbottle.dispatch.rules.base import ABCRule, VBMLRule
from .base import Data, SetRule, MyPatcher
from re import compile, I, S
from vbml import Pattern

custom_rules = SetRule.custom_rules

@SetRule('command')
class CommandVBMLRule(VBMLRule):
	patcher = MyPatcher()

	def __init__(self, pattern):
		regex = r'[\./!:]{}$'

		if isinstance(pattern, str):
			pattern = [Pattern(pattern, regex = regex, flags = I | S)]
		elif isinstance(pattern, Pattern):
			pattern = [pattern]
		elif isinstance(pattern, list):
			pattern = [p if isinstance(p, Pattern) else Pattern(p, regex = regex, flags = I | S) for p in pattern]

		self.patterns = pattern

@SetRule('audio_message')
class AudioMessage(VBMLRule, Data):
	class AM(dict):
		__getattr__ = dict.get

	async def check(self, message):
		if (audio_message := message.attachments and message.attachments[0].audio_message) \
			and (text := self.amessage.get_text(audio_message)): await super().check(self.AM(text = text))

@SetRule('is_admin')
class IsAdmin(ABCRule, Data):
	def __init__(self, adm):
		self.adm = adm

	def check_role(self, message, chat_settings):
		return message.from_id == chat_settings.owner_id or message.from_id in chat_settings.admin_ids

	async def check(self, message):
		if items := (await self.bot.api.messages.get_conversations_by_id(peer_ids = message.peer_id)).items:
			is_admin = self.check_role(message, items[0].chat_settings)
			return self.adm and is_admin or not self.adm and not is_admin

@SetRule('is_owner')
class IsOwner(IsAdmin):
	def check_role(self, message, chat_settings):
		return message.from_id == chat_settings.owner_id

@SetRule('with_text')
class WithText(ABCRule, Data):
	def __init__(self, wt):
		self.wt = wt

	async def check(self, message):
		await self.lvl.hello_text()
		if text := self.lvl.get('HELLO'): text = {'text': text}
		return self.wt and text or not self.wt and not text

@SetRule('with_reply_message')
class WithReplyMessage(ABCRule):
	def __init__(self, wrm):
		self.wrm = wrm

	async def check(self, message):
		is_wrm = message.reply_message and message.reply_message.from_id > 0
		return self.wrm and is_wrm or not self.wrm and not is_wrm

@SetRule('from_id_pos')
class FromIdPos(ABCRule):
	def __init__(self, fip):
		self.fip = fip

	async def check(self, message):
		is_fip = message.from_id > 0
		return self.fip and is_fip or not self.fip and not is_fip

@SetRule('regex')
class RegexRule(ABCRule):
	def __init__(self, regex):
		self.compile = compile(regex, flags = I | S)

	async def check(self, message):
		return bool(self.compile.search(message.text))
