from utils import InitParams

from commands.lvl import LVLCommands
from commands.nick import NickCommands
from commands.extra import ExtraCommands
from commands.shikimori import ShikimoriCommands
from commands.chat_action import ChatActionCommands
from commands.regex import RegexCommands

class HelpCommand(InitParams):
	help = [
		'/Help LVL - уровни',
		'/Help Nick - ники',
		'/Help Extra - доп. команды',
		'/Help Shiki - шикимори'
	]

	dict_help = {
		'lvl': LVLCommands,
		'nick': NickCommands,
		'extra': ExtraCommands,
		'shiki': ShikimoriCommands
	}

	def __init__(self):
		@self.bot.on.chat_message(text = ['help', 'help <extra:inc[lvl,nick,extra,shiki]>'], command = True)
		async def help(message, extra = None):
			await message(f"Команды{f' {extra.title()}' if extra else ''}:\n" + '\n'.join(f'{n + 1}) {comm}' for n, comm in enumerate(self.dict_help.get(extra, self).help)))
