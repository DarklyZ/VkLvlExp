from utils import InitParams
from utils.lvls import atta

class LVLCommands(InitParams):
	help = [
		'/MyLVL - мой уровень',
		'/LVL & <rep_mes> - посмотреть уровень участника',
		'/Tele <count> & <rep_mes> - передать свою exp другому',
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
