from vkbottle.utils import ContextInstanceMixin
from vkbottle.types.base import BaseModel
from aiohttp import request
from init import InitParams
from io import BytesIO

class AMessage(ContextInstanceMixin, InitParams):
	url = 'http://tts.voicetech.yandex.net/tts'

	class params(BaseModel):
		voice = 'alyss'
		emotion = 'evil'
		speed = '1.2'
		text: str

	def __init__(self):
		self.set_current(self)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, text):
		async with request('GET', self.url, params = self.params(text = text).dict()) as response:
			bfile = await response.content.read()
		server = await self.api.docs.get_messages_upload_server(type = 'audio_message', peer_id = self.peer_id)
		async with request('POST', server.upload_url, data = {'file': BytesIO(bfile)}) as response:
			file = (await response.json())['file']
		save = await self.api.docs.save(file = file)
		return f'doc{save.audio_message.owner_id}_{save.audio_message.id}'

	async def get_text(self, audio_message):
		pass

def get_audio_message():
	return AMessage.get_current()