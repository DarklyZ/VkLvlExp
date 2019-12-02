from vk.bot_framework.dispatcher.handler import SkipHandler
from vk.bot_framework import NamedRule, BaseMiddleware
from vk.types.events.community.events_list import Event
from string import punctuation as punc
from json import loads
from extra import atta

def load(dp, vk, lvl_class):
	
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
				data['lvl'] = lvl_class(message.peer_id, message.date)
				await data['lvl'].check_add_user(message.from_id)
				exp = atta(message.text, message.attachments) or None
				if message.payload is None and exp is not None: await data['lvl'].insert_lvl(message.from_id, exp = exp)
			return data
	
	@dp.setup_rule
	class Commands(NamedRule):
		key = 'commands'
		meta = {"deprecated": False}
	    
		def __init__(self, commands):
			self.commands = commands
	
		async def check(self, message, data):
			msg = message.text.lower().split(maxsplit = 1) or None
			return msg is not None and msg[0][0] in punc and msg[0][1:] in self.commands
	
	@dp.setup_rule
	class PayloadCommands(NamedRule):
		key = 'payload_commands'
		meta = {"deprecated": False}
	
		def __init__(self, commands):
			self.commands = commands
	
		async def check(self, message, data):
			return message.payload is not None and loads(message.payload).get('command') in self.commands
	
	@dp.setup_rule
	class IsAdmin(NamedRule):
		key = 'is_admin'
		meta = {"deprecated": False}
	
		def __init__(self, admin):
			self.admin = admin
		
		async def check(self, message, data):
			items = (await vk.api_request('messages.getConversationsById', {'peer_ids': message.peer_id}))['items'] or None
			if items is not None:
				chat_settings = items[0]['chat_settings']
				is_admin = message.from_id == chat_settings['owner_id'] or message.from_id in chat_settings['admin_ids']
				return self.admin and is_admin or not self.admin and not is_admin
			else: return False
	
	return dp