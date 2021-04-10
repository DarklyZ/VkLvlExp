from utils import Data as data
from vkbottle.bot import BotLabeler

help = [
	"/Slave BUY & <rep_mes> - купить раба",
	"/Slave WORK <work> & <rep_mes> - дать рабу работу",
	"/MySlaves - мои рабы",
	"/Slaves & <rep_mes> - рабы"
]

bl = BotLabeler()

@bl.chat_message(command = 'slave buy', with_reply_message = True)
async def slave_buy(message):
	if extra := await data.lvl.slave_buy(id := message.from_id, slave := message.reply_message.from_id):
		await data.lvl.send(id, slave, master := extra[0])
		await message.answer(f"Раб успешно приобретён:\n{data.lvl[slave]}\n{-extra[1]:+}Ⓔ:\n{data.lvl[id]}\n" +
			(f"{extra[1]:+}Ⓔ:\n{data.lvl[master]}" if master else ''))
	else: await message.answer("Недостаточно exp")

@bl.chat_message(command = 'slave work <work>', with_reply_message = True)
async def slave_work(message, work):
	await data.lvl.send(slave := message.reply_message.from_id)
	if await data.lvl.slave_work(message.from_id, slave, work):
		await message.answer(f"Раб:\n{data.lvl[slave]}\nУстроен на работу: {work}")
	else: await message.answer(f"Вы не можете сменить работу у {data.lvl[slave]}")

@bl.chat_message(command = 'myslaves')
async def my_slaves(message):
	await message.answer("Ваши Рабы:\n" + await data.lvl.slaves_by(message.from_id))

@bl.chat_message(command = 'slaves', with_reply_message = True)
async def user_slaves(message):
	await data.lvl.user(id := message.reply_message.from_id)
	await message.answer(f"Рабы у {data.lvl[id]}:\n" + await data.lvl.slaves_by(id))
