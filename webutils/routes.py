from utils import Data as data
from aiohttp.web import RouteTableDef, Response, json_response
from . import Options
from os import getenv

routes = RouteTableDef()

async def user_id(request):
	if key := request.headers.getone('key', False):
		return await data.lvl.join_key(key)

async def chat_settings(request):
	if items := (await data.bot.api.messages.get_conversations_by_id(peer_ids = data.lvl.peer_id)).items:
		return items[0].chat_settings

def params(*keys):
	async def params(request):
		obj = await request.json()
		for key in set(keys):
			if key not in obj: return
		return obj
	return params

@routes.post('/bot')
@Options(params('secret', 'type', 'group_id'))
async def bot(request, params):
	if params['secret'] == getenv('SECRET_KEY'):
		if params['type'] == 'confirmation':
			return Response(text = getenv('CONFIRM_KEY'))
		if request.headers.getone('X-Retry-Counter', False):
			return Response(text = 'ok')

		data.bot.polling.group_id = params['group_id']
		await data.bot.router.route(params, data.bot.api)
		return Response(text = 'ok')

@routes.get('/get_avatar')
async def get_avatar(request):
	return json_response({'response': (await data.bot.api.groups.get_by_id())[0].photo_200})

@routes.post('/get_status')
@Options(user_id, chat_settings)
async def get_status(request, user_id, chat_settings):
	status = 'admin' if user_id == chat_settings.owner_id or user_id in chat_settings.admin_ids else 'user'
	return json_response({'response': {'title': chat_settings.title, 'status': status}})

@routes.post('/get_user')
@Options(user_id)
async def get_user(request, user_id):
	await data.lvl.get_user(user_id)
	return json_response(data.lvl)

@routes.post('/get_top')
@Options(user_id, params('x', 'y'))
async def get_top(request, user_id, params):
	await data.lvl.get_top(params['x'], params['y'])
	return json_response(data.lvl)