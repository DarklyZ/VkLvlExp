from vkbottle.utils import ContextInstanceMixin
from vkbottle.http.request import HTTP
from vkbottle.api import get_api
from io import BytesIO

class AMessage(HTTP, ContextInstanceMixin):
	def __init__(self):
		self.api = get_api()
		self.set_current(self)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, text):
		content = await self.request.get(f'http://tts.voicetech.yandex.net/tts?voice=alena&format=mp3&quality=hi&lang=ru_RU&speed=1.2&text={text}', read_content = True)
		server = await self.api.docs.get_messages_upload_server(type = 'audio_message', peer_id = self.peer_id)
		with BytesIO(content) as f:
			file = (await self.request.post(server.upload_url, data = {'file': f}))['file']
		save = await self.api.docs.save(file = file)
		return f'doc{save.audio_message.owner_id}_{save.audio_message.id}'

def get_audio_message():
	return AMessage.get_current()