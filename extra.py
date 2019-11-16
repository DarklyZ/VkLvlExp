from vk.types.wall_post import WallPost
from itertools import zip_longest
from re import *

def isint(arg):
	try: int(arg)
	except ValueError: return False
	else: return True

def ispos(arg):
	try: return int(arg) >= 0
	except ValueError: return False

def atta(text = '', attachments = [], event_attachments = []):
	s = sum(3 if len(chars) >= 6 else 1 for chars in findall(r'\b[a-zа-яё]{3,}\b', text, I))
	count = s if s < 50 else 50
	for attachment, event_attachment in zip_longest(attachments, event_attachments):
		if attachment.type == 'photo':
			pixel = max(size.width * size.height for size in attachment.photo.sizes)
			count += round(pixel / (1280 * 720 / 70)) if pixel < 1280 * 720 else 70
		elif attachment.type == 'wall' and event_attachment is not None:
			wall = WallPost(**event_attachment['wall'])
			if wall.attachments is not None: count += atta(attachments = wall.attachments)
		elif attachment.type == 'doc' and attachment.doc.ext == 'gif': count += 20
		elif attachment.type == 'audio_message': count += round(attachment.audio_message.duration) if attachment.audio_message.duration < 25 else 25
		elif attachment.type == 'video': count += round(attachment.video.duration / 1.5) if attachment.video.duration < 60 * 2 else 80
		elif attachment.type == 'sticker': count += 10
		elif attachment.type == 'audio': count += round(attachment.audio.duration / 3) if attachment.audio.duration < 60 * 3 else 60
	return count