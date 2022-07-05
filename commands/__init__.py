from utils import custom_rules
from vkbottle.bot import BotLabeler

from . import lvl, nick, extra, chat_action, regex, key, slaves

help_none = [
	"/Help LVL - уровни",
	"/Help Slaves - рабы",
	"/Help Nick - ники",
	"/Help Extra - доп. команды"
]

dict_help = {
	'lvl': lvl.help,
	'slaves': slaves.help,
	'nick': nick.help,
	'extra': extra.help,
}

bl = BotLabeler(custom_rules = custom_rules)

@bl.chat_message(command = ('help', 'help <extra:inc[lvl,slaves,nick,extra]>'))
async def help(message, extra = None):
	await message.answer(f"Команды{f' {extra.title()}' if extra else ''}:\n" + '\n'.join(f'{n + 1}) {comm}' for n, comm in enumerate(dict_help.get(extra, help_none))))

labelers = (bl, lvl.bl, slaves.bl, nick.bl, extra.bl, key.bl, chat_action.bl, regex.bl)
