from vk.bot_framework import NamedRule
from string import punctuation as punc
from json import loads

def load(dp, vk):
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
	class WithPayload(NamedRule):
		key = 'with_payload'
		meta = {"deprecated": False}
	
		def __init__(self, payload):
			self.payload = payload
	
		async def check(self, message, data):
			if self.payload and message.payload is not None : return True
			elif not self.payload and message.payload is None : return True
			else: return False
	
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
			try: chat = (await vk.api_request('messages.getConversationsById', {'peer_ids': message.peer_id}))['items'][0]['chat_settings']
			except: is_admin = False
			else: is_admin = message.from_id == chat['owner_id'] or message.from_id in chat['admin_ids']
			if self.admin and is_admin: return True
			elif not self.admin and not is_admin: return True
			else: return False
	
	return dp