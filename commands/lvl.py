from utils import InitData
from pyaspeller import YandexSpeller
from re import split, I

class YaSpeller(YandexSpeller):
	def spell(self, text):
		text = self._prepare_text(text)

		if text:
			for item in self._spell_text(text):
				yield item
		else:
			raise NotImplementedError()

speller = YaSpeller()

def atta(text='', attachments=[], negative = False, return_errors = False):
	if text:
		dict_errors = {change['word']: change['s'] for change in speller.spell(text)}
		s = sum(3 if len(chars) >= 6 else 1 for chars in split(r'[^a-zа-яё]+', text, flags=I) if
		        len(chars) >= 3 and chars not in dict_errors)
		count = s if s < 50 else 50
	else:
		count, dict_errors = 0, {}

	for attachment in attachments:
		if attachment.type == 'photo':
			pixel = max(size.width * size.height for size in attachment.photo.sizes)
			count += round(pixel * 50 / (1280 * 720)) if pixel < 1280 * 720 else 50
		elif attachment.type == 'wall':
			count += atta(attachment.wall.text, attachment.wall.attachments)
		elif attachment.type == 'wall_reply':
			count += atta(attachment.wall_reply.text, attachment.wall_reply.attachments)
		elif attachment.type == 'doc' and attachment.doc.ext == 'gif':
			count += 20
		elif attachment.type == 'audio_message':
			count += attachment.audio_message.duration if attachment.audio_message.duration < 25 else 25
		elif attachment.type == 'video':
			count += round(attachment.video.duration * 80 / 30) if attachment.video.duration < 30 else 80
		elif attachment.type == 'sticker':
			count += 10
		elif attachment.type == 'audio':
			count += round(attachment.audio.duration * 60 / 180) if attachment.audio.duration < 180 else 60
	count *= -1 if negative else 1
	return (count, dict_errors) if return_errors else count

class LVLCommands(InitData.Data):
	help = [
		'/MyLVL - мой уровень',
		'/LVL & <rep_mes> - посмотреть уровень участника',
		'/Tele <count> & <rep_mes> - передать свою exp другому',
		'/TopLVL[ <от> <до>] - топ 10 участников',
		'/TopTemp[ <от> <до>] - временный топ 10 участников',
		'/Info & <rep_mes> - узнать вес сообщения'
	]

	def __init__(self):
		@self.bot.on.chat_message(text = 'mylvl', command = True)
		async def mylvl(message):
			await self.lvl_class.send(id := message.from_id)
			await message(self.lvl_class[id])

		@self.bot.on.chat_message(text = 'lvl', command = True, with_reply_message = True)
		async def lvl(message):
			await self.lvl_class.send(id := message.reply_message.from_id)
			await message(self.lvl_class[id])

		@self.bot.on.chat_message(text = ['tele <exp:pos>', 'tele <exp:inc[up]>'], command = True, with_reply_message = True, from_id_pos = True)
		async def tele(message, exp):
			if exp == 'up': exp = atta(message.reply_message.text, message.reply_message.attachments)
			if await self.lvl_class.remove_exp(id1 := message.from_id, exp = exp):
				await self.lvl_class.update_lvl(id2 := message.reply_message.from_id, exp = exp)
				await self.lvl_class.send(id1, id2)
				blank = f"{exp:+}Ⓔ:\n{self.lvl_class[id2]}\n{-exp:+}Ⓔ:\n{self.lvl_class[id1]}"
			else:
				await self.lvl_class.send(id1)
				blank = f"Не хватает Ⓔ!\n{self.lvl_class[id1]}"
			await message(blank)

		@self.bot.on.chat_message(text = ['exp <exp:int>', 'exp <exp:inc[up,down]>', 'exp <lvl:int> <exp:int>'], command = True, is_admin = True, with_reply_message = True)
		async def exp(message, exp, lvl = 0):
			if exp in ('up', 'down'): exp = atta(message.reply_message.text, message.reply_message.attachments, exp == 'down')
			await self.lvl_class.update_lvl(id := message.reply_message.from_id, exp = exp, lvl = lvl)
			await self.lvl_class.send(id)
			await message((f"{lvl:+}Ⓛ|" if lvl else '') + f"{exp:+}Ⓔ:\n" + self.lvl_class[id])

		@self.bot.on.chat_message(text = 'info', command = True, with_reply_message = True)
		async def info(message):
			exp, errors = atta(message.reply_message.text, message.reply_message.attachments, return_errors = True)
			extra = '\nВозможные ошибки:\n' + ' / '.join(f"{err} -> {', '.join(errors[err])}" if errors[err] else err for err in errors) if errors else ''
			await message(f"Стоимость сообщения {exp:+}Ⓔ" + extra)

		@self.bot.on.chat_message(text = ['toplvl <one:pos> <two:pos>', 'toplvl'], command = True)
		async def toplvl_send(message, one = 1, two = 10):
			await message(await self.lvl_class.toplvl_size(one, two), disable_mentions = True)

		@self.bot.on.chat_message(text = ['toptemp <one:pos> <two:pos>', 'toptemp'], command = True)
		async def toptemp_send(message, one = 1, two = 10):
			await message(await self.lvl_class.toptemp_size(one, two), disable_mentions = True)