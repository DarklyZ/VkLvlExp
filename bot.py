from logging import basicConfig
from vk import VK
from vk.bot_framework import Dispatcher
from vk.utils import TaskManager
from lvls import LVL
from os import getenv

basicConfig(level="INFO")

vk, group_id, database_url = VK(getenv('TOKEN')), getenv('GROUP_ID'), getenv('DATABASE_URL')
task_manager = TaskManager(vk.loop)
lvl_class = LVL(vk, database_url)
dp = Dispatcher(vk)

import middleware_rules, bot_commands, chat_action_commands, regex_commands
dp = middleware_rules.load(dp, vk, lvl_class)
dp = bot_commands.load(dp, vk)
dp = chat_action_commands.load(dp, vk, group_id)
dp = regex_commands.load(dp, group_id)

@task_manager.add_task
async def run():
	dp.run_polling(group_id)

async def on_shutdown():
	await vk.close()
	await lvl_class.close_db()

if __name__ == "__main__":
	task_manager.run_task(lvl_class.connect_db)
	task_manager.run(auto_reload = True, on_shutdown = on_shutdown)
