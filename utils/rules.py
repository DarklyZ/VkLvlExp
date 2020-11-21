from vkbottle.dispatch.rules.bot import ABCMessageRule, ChatActionRule, VBMLRule
from vkbottle_types.objects import MessagesMessageActionStatus as MMAS
from utils import InitData
from re import compile, I, S
from sys import modules

from vbml import Pattern

class SetRule:
	DEFAULT_CUSTOM_RULES = modules['vkbottle.framework.bot.labeler.default'].DEFAULT_CUSTOM_RULES

	def __init__(self, name):
		self.name = name

	def __call__(self, cls):
		self.DEFAULT_CUSTOM_RULES[self.name] = cls
		return cls

@SetRule('command')
class CommandVBMLRule(VBMLRule):
	def __init__(self, pattern):
		self.config['vbml_flags'] = I | S

		regex = r'[\./!:]{}$'

		if isinstance(pattern, str):
			pattern = [Pattern(pattern, regex = regex, flags = self.config['vbml_flags'])]
		elif isinstance(pattern, Pattern):
			pattern = [pattern]
		elif isinstance(pattern, list):
			pattern = [p if isinstance(p, Pattern) else Pattern(p, regex = regex, flags = self.config['vbml_flags']) for p in pattern]

		self.patterns = pattern
		self.patcher = self.config["vbml_patcher"]

@SetRule('audio_message')
class AudioMessage(VBMLRule, InitData.Data):
	class AM(dict):
		__getattr__ = dict.get

	async def check(self, message):
		if (audio_message := message.attachments and message.attachments[0].audio_message) \
			and (text := self.amessage.get_text(audio_message)): await super().check(self.AM(text = text))

@SetRule('is_admin')
class IsAdmin(ABCMessageRule, InitData.Data):
	def __init__(self, adm):
		self.adm = adm

	async def check(self, message):
		if items := (await self.bot.api.messages.get_conversations_by_id(peer_ids = message.peer_id)).items:
			chat_settings = items[0].chat_settings
			is_admin = message.from_id == chat_settings.owner_id or message.from_id in chat_settings.admin_ids
			return self.adm and is_admin or not self.adm and not is_admin

@SetRule('with_text')
class WithText(ABCMessageRule, InitData.Data):
	def __init__(self, wt):
		self.wt = wt

	async def check(self, message):
		if text := await self.lvl_class.hello_text(): text = {'text': text}
		return self.wt and text or not self.wt and not text

@SetRule('with_reply_message')
class WithReplyMessage(ABCMessageRule):
	def __init__(self, wrm):
		self.wrm = wrm
	
	async def check(self, message):
		is_wrm = message.reply_message and message.reply_message.from_id > 0
		return self.wrm and is_wrm or not self.wrm and not is_wrm

@SetRule('from_id_pos')
class FromIdPos(ABCMessageRule):
	def __init__(self, fip):
		self.fip = fip
	
	async def check(self, message):
		is_fip = message.from_id > 0
		return self.fip and is_fip or not self.fip and not is_fip

@SetRule('regex')
class RegexRule(ABCMessageRule):
	def __init__(self, regex):
		self.compile = compile(regex, flags = I | S)

	async def check(self, message):
		return bool(self.compile.search(message.text))

@SetRule('chat_action_rule')
class ChatActionRule(ChatActionRule):
	def __init__(self, arg):
		super().__init__([arg] if isinstance(arg, MMAS) else arg)