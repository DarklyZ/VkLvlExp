from utils import InitParams
from io import BytesIO
from aiohttp import request

class ShikiApi(InitParams):
	url = 'http://shikimori.one/api/{method}'

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def search(self, type, text):
		if type == 'characters': type += '/search'
		async with request('GET', self.url.format(method = type), params = {'search': text}) as response:
			return await response.json()

	async def get_doc(self, urls):
		server = await self.api.photos.get_messages_upload_server(peer_id = self.peer_id)
		saves = []
		for url in urls:
			async with request('GET', 'http://shikimori.one' + url) as response:
				with BytesIO(await response.read()) as bfile:
					bfile.name = '.jpg'
					async with request('POST', server.upload_url, data = {'photo': bfile}) as response:
						res = await response.json(content_type = 'text/html')
						saves.append(await self.api.photos.save_messages_photo(server = res['server'], photo = res['photo'], hash = res['hash']))
		return [f'photo{save[0].owner_id}_{save[0].id}' for save in saves]

class AMessage(InitParams):
	url = 'http://tts.voicetech.yandex.net/tts'

	class Params(dict):
		val = {'voice': 'alyss', 'emotion': 'evil', 'speed': '1.1'}
		__init__ = lambda self, **var: super().__init__(**self.val, **var)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, text):
		server = await self.api.docs.get_messages_upload_server(type = 'audio_message', peer_id = self.peer_id)
		async with request('GET', self.url, params = self.Params(text = text)) as response:
			with BytesIO(await response.read()) as bfile:
				async with request('POST', server.upload_url, data = {'file': bfile}) as response:
					save = await self.api.docs.save(file = (await response.json())['file'])
		return f'doc{save.audio_message.owner_id}_{save.audio_message.id}'

	async def get_text(self, audio_message):
		pass

class ThisWaifuDoesNotExist(InitParams):
	url = 'https://www.thiswaifudoesnotexist.net/example-{id}.jpg'

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, id):
		server = await self.api.photos.get_messages_upload_server(peer_id = self.peer_id)
		async with request('GET', self.url.format(id = id)) as response:
			with BytesIO(await response.read()) as bfile:
				bfile.name = '.jpg'
				async with request('POST', server.upload_url, data = {'photo': bfile}) as response:
					res = await response.json(content_type = 'text/html')
					save = await self.api.photos.save_messages_photo(server = res['server'], photo = res['photo'], hash = res['hash'])
		return f'photo{save[0].owner_id}_{save[0].id}'