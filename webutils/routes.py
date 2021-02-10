from utils import Data as data
from aiohttp.web import RouteTableDef, Response, json_response
from . import options
from os import getenv

routes = RouteTableDef()

async def user_id(request):
	if key := request.headers.getone('key', False):
		return await data.lvl.join_key(key)

def params(*keys):
	async def params(request):
		obj = await request.json()
		for key in set(keys):
			if key not in obj: return
		return obj
	return params

@routes.post('/bot')
@options(params('secret', 'type', 'group_id'))
async def bot(request, params):
	if params['secret'] == getenv('SECRET_KEY'):
		if params['type'] == 'confirmation':
			return Response(text = getenv('CONFIRM_KEY'))
		if request.headers.getone('X-Retry-Counter', False):
			return Response(text = 'ok')

		data.bot.polling.group_id = params['group_id']
		await data.bot.router.route(params, data.bot.api)
		return Response(text = 'ok')

@routes.post('/get_lvl')
@options(user_id)
async def get_lvl(request, user_id):
	await data.lvl.get_lvl(user_id)
	return json_response(data.lvl)

@routes.post('/get_top')
@options(user_id, params('x', 'y'))
async def get_top(request, user_id, params):
	await data.lvl.get_top(params['x'], params['y'])
	return json_response(data.lvl)