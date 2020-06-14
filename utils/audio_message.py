from vkbottle.utils import ContextInstanceMixin
from aiohttp import request
from utils import InitParams
from io import BytesIO

class AMessage(ContextInstanceMixin, InitParams):
	url = 'http://tts.voicetech.yandex.net/tts'

	class Params(dict):
		val = {'voice': 'alyss', 'emotion': 'evil', 'speed': '1.2'}
		__init__ = lambda self, **var: super().__init__(**self.val, **var)

	def __init__(self):
		self.set_current(self)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, text):
		server = await self.api.docs.get_messages_upload_server(type = 'audio_message', peer_id = self.peer_id)
		async with request('GET', self.url, params = self.Params(text = text)) as response:
			with BytesIO(await response.content.read()) as bfile:
				async with request('POST', server.upload_url, data = {'file': bfile}) as response:
					save = await self.api.docs.save(file = (await response.json())['file'])
		return f'doc{save.audio_message.owner_id}_{save.audio_message.id}'

	async def get_text(self, audio_message):
		pass

def get_amessage():
	return AMessage.get_current()