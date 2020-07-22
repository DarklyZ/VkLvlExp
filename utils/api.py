from utils import InitParams
from io import BytesIO
from aiohttp import request

class ShikiApi(InitParams):
	url_shiki = 'http://shikimori.one{url}'
	url_shiki_api = url_shiki.format(url = '/api/{method}')
	url_neko_anime = 'https://nekomori.ch/anime/-{id}/general'

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def search(self, type, text, page, limit = 5):
		params, types = {'search': text}, ['chatacters', 'people']
		if type not in types: params.update({'censored': 'false', 'page': page, 'limit': str(limit)})
		async with request('GET', self.url_shiki_api.format(method = type + ('/search' if type in types else '')), params = params) as response:
			res = await response.json()
			return res[(page - 1) * limit : (page - 1) * limit + limit] if type in types else res

	async def get_shiki_short_link(self, url):
		return (await self.bot.api.utils.get_short_link(self.url_shiki.format(url = url))).short_url[8:]

	async def get_neko_short_link(self, id):
		return (await self.bot.api.utils.get_short_link(self.url_neko_anime.format(id = id))).short_url[8:]

	async def get_doc(self, urls):
		server = await self.bot.api.photos.get_messages_upload_server(peer_id = self.peer_id)
		saves = []
		for url in urls:
			async with request('GET', 'http://shikimori.one' + url) as response:
				with BytesIO(await response.read()) as bfile:
					bfile.name = '.jpg'
					async with request('POST', server.upload_url, data = {'photo': bfile}) as response:
						res = await response.json(content_type = 'text/html')
						saves.append(await self.bot.api.photos.save_messages_photo(server = res['server'], photo = res['photo'], hash = res['hash']))
		return [f'photo{save[0].owner_id}_{save[0].id}' for save in saves]

class AMessage(InitParams):
	url = 'http://tts.voicetech.yandex.net/tts'

	class Params(dict):
		val = {'voice': 'alyss', 'emotion': 'evil', 'speed': '1.1'}
		__init__ = lambda self, **var: super().__init__(**self.val, **var)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, text):
		server = await self.bot.api.docs.get_messages_upload_server(type = 'audio_message', peer_id = self.peer_id)
		async with request('GET', self.url, params = self.Params(text = text)) as response:
			with BytesIO(await response.read()) as bfile:
				async with request('POST', server.upload_url, data = {'file': bfile}) as response:
					save = await self.bot.api.docs.save(file = (await response.json())['file'])
		return f'doc{save.audio_message.owner_id}_{save.audio_message.id}'

	async def get_text(self, audio_message):
		pass

class ThisWaifuDoesNotExist(InitParams):
	url = 'https://www.thiswaifudoesnotexist.net/example-{id}.jpg'

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, id):
		server = await self.bot.api.photos.get_messages_upload_server(peer_id = self.peer_id)
		async with request('GET', self.url.format(id = id)) as response:
			with BytesIO(await response.read()) as bfile:
				bfile.name = '.jpg'
				async with request('POST', server.upload_url, data = {'photo': bfile}) as response:
					res = await response.json(content_type = 'text/html')
					save = await self.bot.api.photos.save_messages_photo(server = res['server'], photo = res['photo'], hash = res['hash'])
		return f'photo{save[0].owner_id}_{save[0].id}'

class Foaf(InitParams):
	url = 'https://vk.com/foaf.php'

	async def __call__(self, id):
		async with request('GET', self.url, params = {'id': str(id)}) as response:
			return await response.text('WINDOWS-1251')