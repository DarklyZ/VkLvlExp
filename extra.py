from vkbottle.rule import AbstractMessageRule
from re import findall, I

class IsAdmin(AbstractMessageRule):
	def __init__(self, adm):
		self.adm = adm

	@classmethod
	def set_api(cls, api):
		cls.api = api

	async def check(self, message):
		items = (await self.api.messages.getConversationsById(peer_ids = message.peer_id))['items']
		if not items: return False
		chat_settings = items[0]['chat_settings']
		is_admin = message.from_id == chat_settings['owner_id'] or message.from_id in chat_settings['admin_ids']
		return self.adm and is_admin or not self.adm and not is_admin

class WithText(AbstractMessageRule):
	def __init__(self, wt):
		self.wt = wt

	@classmethod
	def set_lvl(cls, lvl_class):
		cls.lvl_class = lvl_class

	async def check(self, message):
		text = await self.lvl_class.hello_text()
		if self.wt and text:
			self.context.kwargs = {'text': text}
			return True
		elif not self.wt and not text: return True
		else: return False

class WithReplyMessage(AbstractMessageRule):
	def __init__(self, wrm):
		self.wrm = wrm
	
	async def check(self, message):
		is_wrm = message.reply_message and message.reply_message.from_id > 0
		return self.wrm and is_wrm or not self.wrm and not is_wrm

class FromIdPos(AbstractMessageRule):
	def __init__(self, fip):
		self.fip = fip
	
	async def check(self, message):
		is_fip = message.from_id > 0
		return self.fip and is_fip or not self.fip and not is_fip

def atta(text = '', attachments = []):
	s = sum(3 if len(chars) >= 6 else 1 for chars in findall(r'\b[a-zа-яё]{3,}\b', text, I))
	count = s if s < 50 else 50
	for attachment in attachments:
		if attachment.type == 'photo':
			pixel = max(size.width * size.height for size in attachment.photo.sizes)
			count += round(pixel / (1280 * 720 / 70)) if pixel < 1280 * 720 else 70
		elif attachment.type == 'wall': count += 40
		elif attachment.type == 'doc' and attachment.doc.ext == 'gif': count += 20
		elif attachment.type == 'audio_message': count += round(attachment.audio_message.duration) if attachment.audio_message.duration < 25 else 25
		elif attachment.type == 'video': count += round(attachment.video.duration / 1.5) if attachment.video.duration < 60 * 2 else 80
		elif attachment.type == 'sticker': count += 10
		elif attachment.type == 'audio': count += round(attachment.audio.duration / 3) if attachment.audio.duration < 60 * 3 else 60
	return count