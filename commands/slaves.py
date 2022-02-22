from utils import Data as data
from utils.rules import custom_rules
from vkbottle.bot import BotLabeler

help = [
	"/Slave BUY & <rep_mes> - купить раба",
	"/Slave WORK <work> & <rep_mes> - дать рабу работу",
	"/MySlaves - мои рабы",
	"/Slaves & <rep_mes> - рабы"
]

bl = BotLabeler(custom_rules = custom_rules)

@bl.chat_message(command = 'slave buy', with_reply_message = True)
async def slave_buy(message):
	master, price = await data.lvl.slave_buy(id := message.from_id, slave := message.reply_message.from_id)
	await data.lvl.send(*filter(bool, (id, slave, master)))
	await message.answer(f"Раб успешно приобретён:\n{data.lvl[slave]}\n{-price:+}Ⓔ:\n{data.lvl[id]}\n" +
		(f"{extra[1]:+}Ⓔ:\n{data.lvl[master]}" if master else ''))

@bl.chat_message(command = 'slave work <work:max[20]>', with_reply_message = True)
async def slave_work(message, work):
	await data.lvl.slave_work(message.from_id, slave, work, data.lvl[slave])
	await data.lvl.send(slave := message.reply_message.from_id)
	await message.answer(f"Раб:\n{data.lvl[slave]}\nУстроен на работу: {work}")

@bl.chat_message(command = 'myslaves')
async def my_slaves(message):
	await data.lvl.slaves_by(id := message.from_id)
	await message.answer("Ваши Рабы:\n" + data.lvl['SLAVES'])

@bl.chat_message(command = 'slaves', with_reply_message = True)
async def user_slaves(message):
	await data.lvl.user(id := message.reply_message.from_id)
	await data.lvl.slaves_by(id)
	await message.answer(f"Рабы у {data.lvl[id]}:\n" + data.lvl['SLAVES'])