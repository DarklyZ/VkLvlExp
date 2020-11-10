from utils import InitData
from vkbottle.bot import BotLabeler

from . import lvl, nick, extra, chat_action, regex

help_none = [
	'/Help LVL - уровни',
	'/Help Nick - ники',
	'/Help Extra - доп. команды'
]

dict_help = {
	'lvl': lvl.help,
	'nick': nick.help,
	'extra': extra.help,
}

with InitData.With as data:
	bl = BotLabeler()

	@bl.chat_message(command = ['help', 'help <extra:inc[lvl,nick,extra]>'])
	async def help(message, extra = None):
		await message.answer(f"Команды{f' {extra.title()}' if extra else ''}:\n" + '\n'.join(f'{n + 1}) {comm}' for n, comm in enumerate(dict_help.get(extra, help_none))))

labelers = [bl, lvl.bl, nick.bl, extra.bl, chat_action.bl, regex.bl]