from datetime import datetime, tzinfo, timedelta
from .base import Data

@object.__new__
class DateTools:
	@tzinfo.__new__
	class tz(tzinfo):
		utcoffset = lambda self, dt: timedelta(hours = 5)
		dst = lambda self, dt: timedelta()
		tzname = lambda self, dt: '+05:00'

	@property
	def now(self):
		return datetime.now(self.tz)

@object.__new__
class AttachmentsTools(Data):
	async def exp(self, text = '', attachments = [], negative = False, return_errors = False):
		if text:
			dict_errors = {change['word']: change['s'] for change in await self.speller.spell(text)}
			s = sum(3 if len(chars) >= 6 else 1 for chars in split(r'[^a-zа-яё]+', text, flags = I) if len(chars) >= 3 and chars not in dict_errors)
			count = s if s < 50 else 50
		else:
			count, dict_errors = 0, {}

		for attachment in attachments:
			match attachment.type.value:
				case 'photo':
					pixel = max(size.width * size.height for size in attachment.photo.sizes)
					count += round(pixel * 50 / (1280 * 720)) if pixel < 1280 * 720 else 50
				case 'wall':
					count += await self.exp(attachment.wall.text, attachment.wall.attachments or [])
				case 'wall_reply':
					count += await self.exp(attachment.wall_reply.text, attachment.wall_reply.attachments or [])
				case 'audio_message':
					count += attachment.audio_message.duration if attachment.audio_message.duration < 25 else 25
				case 'video':
					count += round(attachment.video.duration * 80 / 30) if attachment.video.duration < 30 else 80
				case 'audio':
					count += round(attachment.audio.duration * 60 / 180) if attachment.audio.duration < 180 else 60
				case 'doc' if attachment.doc.ext == 'gif': count += 20
				case 'sticker': count += 10

		count *= -1 if negative else 1
		return (count, dict_errors) if return_errors else count

@object.__new__
class LVLTools(DateTools.__class__):
	boost = {1: 2, 3: 2, 5: 1, 7: 1}
	stop = {1: '🥇', 2: '🥈', 3: '🥉'}
	sboost = {1: '❸', 3: '❸', 5: '❷', 7: '❷'}

	def cake(self, bdate):
		if isinstance(bdate, str):
			bdate = datetime.strptime(bdate, '%d.%m' if bdate.count('.') == 1 else '%d.%m.%Y')
			return '🎂' if bdate.day == self.now.day and bdate.month == self.now.month else ''
		return ''

	def price(self, slcount, lvl):
		if slcount == 0: return 120
		elif (price := round((1.1 ** slcount - 1) * 1e4)) < (maxexp := lvl * 2000 - 50):
			return price
		return maxexp

	def percent(self, slcounts):
		return percent if (percent := 5 * slcounts + 5) < 50 else 50
