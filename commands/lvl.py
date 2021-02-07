from utils import Data as data
from vkbottle.bot import BotLabeler

help = [
	'/MyLVL - мой уровень',
	'/LVL & <rep_mes> - посмотреть уровень участника',
	'/Tele <count> & <rep_mes> - передать свою exp другому',
	'/TopLVL[ <от> <до>] - топ 10 участников',
	'/TopTemp[ <от> <до>] - временный топ 10 участников',
	'/Info & <rep_mes> - узнать вес сообщения'
]
bl = BotLabeler()

@bl.chat_message(command = 'mylvl')
async def mylvl(message):
	await data.lvlbot.send(id := message.from_id)
	await message.answer(data.lvlbot[id])

@bl.chat_message(command = 'lvl', with_reply_message = True)
async def lvl(message):
	await data.lvlbot.send(id := message.reply_message.from_id)
	await message.answer(data.lvlbot[id])

@bl.chat_message(command = ['tele <exp:pos>', 'tele <exp:inc[up]>'], with_reply_message = True, from_id_pos = True)
async def tele(message, exp):
	if exp == 'up': exp = await data.lvlbot.atta(message.reply_message.text, message.reply_message.attachments)
	if await data.lvlbot.remove_exp(id1 := message.from_id, exp = exp):
		await data.lvlbot.update_lvl(id2 := message.reply_message.from_id, exp = exp)
		await data.lvlbot.send(id1, id2)
		blank = f"{exp:+}Ⓔ:\n{data.lvlbot[id2]}\n{-exp:+}Ⓔ:\n{data.lvlbot[id1]}"
	else:
		await data.lvlbot.send(id1)
		blank = f"Не хватает Ⓔ!\n{data.lvlbot[id1]}"
	await message.answer(blank)

@bl.chat_message(command = ['exp <exp:int>', 'exp <exp:inc[up,down]>', 'exp <lvl:int> <exp:int>'], is_admin = True, with_reply_message = True)
async def exp(message, exp, lvl = 0):
	if exp in ('up', 'down'): exp = await data.lvlbot.atta(message.reply_message.text, message.reply_message.attachments, exp == 'down')
	await data.lvlbot.update_lvl(id := message.reply_message.from_id, exp = exp, lvl = lvl)
	await data.lvlbot.send(id)
	await message.answer((f"{lvl:+}Ⓛ|" if lvl else '') + f"{exp:+}Ⓔ:\n" + data.lvlbot[id])

@bl.chat_message(command = 'info', with_reply_message = True)
async def info(message):
	exp, errors = await data.lvlbot.atta(message.reply_message.text, message.reply_message.attachments, return_errors = True)
	extra = '\nВозможные ошибки:\n' + ' / '.join(f"{err} -> {', '.join(errors[err])}" if errors[err] else err for err in errors) if errors else ''
	await message.answer(f"Стоимость сообщения {exp:+}Ⓔ" + extra)

@bl.chat_message(command = ['toplvl <one:pos> <two:pos>', 'toplvl'])
async def toplvl_send(message, one = 1, two = 10):
	await message.answer(await data.lvlbot.toplvl_size(one, two), disable_mentions = True)

@bl.chat_message(command = ['toptemp <one:pos> <two:pos>', 'toptemp'])
async def toptemp_send(message, one = 1, two = 10):
	await message.answer(await data.lvlbot.toptemp_size(one, two), disable_mentions = True)