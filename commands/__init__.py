from utils import InitParams

from .lvl import LVLCommands
from .top import TopCommands
from .nick import NickCommands
from .extra import ExtraCommands
from .shikimori import ShikimoriCommands
from .chat_action import ChatActionCommands
from .regex import RegexCommands

class HelpCommand(InitParams):
	help = [
		'/Help Top - топ',
		'/Help LVL - уровни',
		'/Help Nick - ники',
		'/Help Extra - доп. команды'
	]

	dict_help = {
		'top': TopCommands,
		'lvl': LVLCommands,
		'nick': NickCommands,
		'extra': ExtraCommands
	}

	def __init__(self):
		@self.bot.on.chat_message(text = ['help', 'help <extra:inc[top,lvl,nick,extra]>'], command = True)
		async def help(message, extra = None):
			await message('Команды:\n' + '\n'.join(f'{n + 1}) {comm}' for n, comm in enumerate(self.dict_help.get(extra, self).help)))
