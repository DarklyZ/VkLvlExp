from utils import Data as data
from aiohttp.web import RouteTableDef, Response, json_response
from . import Options
from os import getenv

routes = RouteTableDef()

@routes.post('/bot')
@Options(rules = {'secret_key'}, keys = {'secret', 'type'})
async def bot(request, body, secret_key):
	if body['type'] == 'confirmation':
		return Response(text = getenv('CONFIRM_KEY'))
	if request.headers.getone('X-Retry-Counter', False):
		return Response(text = 'ok')

	await data.bot.process_event(body)
	return Response(text = 'ok')

@routes.get('/get_avatar')
async def get_avatar(request):
	return json_response({'response': (await data.bot.api.groups.get_by_id())[0].photo_200})

@routes.post('/get_status')
@Options(rules = {'user_id', 'chat_settings'})
async def get_status(request, user_id, chat_settings):
	status = 'admin' if user_id == chat_settings.owner_id or user_id in chat_settings.admin_ids else 'user'
	return json_response({'response': {'title': chat_settings.title, 'status': status}})

@routes.post('/get_user')
@Options(rules = {'user_id'})
async def get_user(request, user_id):
	await data.lvl.get_user(user_id)
	return json_response(data.lvl)

@routes.post('/get_top')
@Options(rules = {'user_id'}, keys = {'x', 'y'})
async def get_top(request, body, user_id):
	await data.lvl.get_top(body['x'], body['y'])
	return json_response(data.lvl)