from logging import basicConfig
from vk import VK
from vk.bot_framework import Dispatcher, BaseMiddleware
from vk.bot_framework.dispatcher.handler import SkipHandler
from vk.types.events.community.events_list import Event
from vk.utils import TaskManager
from lvls import LVL
from os import getenv
from extra import atta

basicConfig(level="INFO")

vk, group_id, database_url = VK(getenv('TOKEN')), getenv('GROUP_ID'), getenv('DATABASE_URL')
task_manager = TaskManager(vk.loop)
dp = Dispatcher(vk)
lvl_class = LVL(vk)

@dp.middleware()
class Regist(BaseMiddleware):
	meta = {"deprecated": False}
	
	async def pre_process_event(self, event, data):
		if event.type == Event.MESSAGE_NEW and event.object.message.from_id != event.object.message.peer_id:
			message = event.object.message
			if (message.from_id < 0 or 
				message.reply_message is not None and
				message.reply_message.from_id < 0 or
				message.action is not None and
				message.action.member_id < 0): raise SkipHandler
			data['lvl'] = lvl_class(message.peer_id)
			await data['lvl'].check_add_user(message.from_id)
			if message.payload is None: await data['lvl'].insert_lvl(message.from_id, exp = atta(message.text, message.attachments))
		return data

import rules
dp = rules.load(dp, vk)

import bot_commands
dp = bot_commands.load(dp, vk)

import chat_action_commands
dp = chat_action_commands.load(dp, vk, group_id)

import regex_commands
dp = regex_commands.load(dp, group_id)

@task_manager.add_task
async def run():
	await lvl_class.connect_db(database_url)
	dp.run_polling(group_id)

async def on_shutdown():
	await vk.close()
	await lvl_class.close_db()

if __name__ == "__main__":
	task_manager.run(on_shutdown = on_shutdown)
