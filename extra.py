from vkbottle.rule import AbstractMessageRule
from re import findall, I

async def is_admin(message):
	items = (await message.api[0].messages.getConversationsById(peer_ids = message.peer_id))['items'] or None
	if not items: return
	chat_settings = items[0]['chat_settings']
	return message.from_id == chat_settings['owner_id'] or message.from_id in chat_settings['admin_ids']

class with_reply_message(AbstractMessageRule):
	def __init__(self, wrm):
		self.wrm = wrm
	
	def check(self, message):
		is_wrm = message.reply_message and message.reply_message.from_id > 0
		return self.wrm and is_wrm or not self.wrm and not is_wrm

class from_id_pos(AbstractMessageRule):
	def __init__(self, fip):
		self.fip = fip
	
	def check(self, message):
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