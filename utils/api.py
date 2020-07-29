from utils import InitData
from io import BytesIO
from aiohttp import request

class YaSpeller:
	api = 'http://speller.yandex.net/services/spellservice.json/checkText'

	def __init__(self, lang = None, ignore_urls = False, ignore_capitalization = False,
			ignore_digits = False, ignore_latin = False, ignore_roman_numerals = False,
			ignore_uppercase = False, find_repeat_words = False, flag_latin = False,
			by_words = False):

		self.lang = lang or ['en', 'ru']

		self.options = 0
		if ignore_uppercase: self.options |= 1
		if ignore_digits: self.options |= 2
		if ignore_urls: self.options |= 4
		if find_repeat_words: self.options |= 8
		if ignore_latin: self.options |= 16
		if flag_latin: self.options |= 128
		if by_words: self.options |= 256
		if ignore_capitalization: self.options |= 512
		if ignore_roman_numerals: self.options |= 2048

	async def spell(self, text):
		lang = ','.join(self.lang)
		data = {
			'text': text,
			'options': self.options,
			'lang': lang,
		}
		async with request('POST', self.api, data = data) as response:
			return await response.json()

class ShikiApi(InitData.Data):
	url_shiki = 'http://shikimori.one{url}'
	url_shiki_api = url_shiki.format(url = '/api/{method}')
	url_neko_anime = 'https://nekomori.ch/anime/-{id}/general'

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def search(self, type, text, page, limit = 5):
		data, types = {'search': text}, ['characters', 'people']
		if type not in types: data.update({'censored': 'false', 'page': page, 'limit': str(limit)})
		else: type += '/search'
		async with request('GET', self.url_shiki_api.format(method = type), data = data) as response:
			res = await response.json()
			return res[(page - 1) * limit : (page - 1) * limit + limit] if len(data) == 1 else res

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

class AMessage(InitData.Data):
	url = 'http://tts.voicetech.yandex.net/tts'
	data = {'voice': 'alyss', 'emotion': 'evil', 'speed': 1.1}

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, text):
		server = await self.bot.api.docs.get_messages_upload_server(type = 'audio_message', peer_id = self.peer_id)
		async with request('GET', self.url, data = {'text': text, **self.data}) as response:
			with BytesIO(await response.read()) as bfile:
				async with request('POST', server.upload_url, data = {'file': bfile}) as response:
					save = await self.bot.api.docs.save(file = (await response.json())['file'])
		return f'doc{save.audio_message.owner_id}_{save.audio_message.id}'

	async def get_text(self, audio_message):
		pass

class ThisWaifuDoesNotExist(InitData.Data):
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

class FoafPHP(InitData.Data):
	url = 'https://vk.com/foaf.php'

	async def __call__(self, id):
		async with request('GET', self.url, params = {'id': str(id)}) as response:
			return await response.text('WINDOWS-1251')