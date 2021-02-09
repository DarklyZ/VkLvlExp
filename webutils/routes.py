from utils import Data as data
from aiohttp.web import RouteTableDef, Response, json_response
from os import getenv

routes = RouteTableDef()

async def join_key(request):
	if key := request.headers.getone('key', False):
		return await data.lvl.join_key(key)

@routes.post('/bot')
async def bot(request):
	params = await request.json()
	if params.get('secret') == getenv('SECRET_KEY'):
		if params['type'] == 'confirmation':
			return Response(text = getenv('CONFIRM_KEY'))
		if request.headers.getone('X-Retry-Counter', False):
			return Response(text = 'ok')

		data.bot.polling.group_id = params['group_id']
		await data.bot.router.route(params, data.bot.api)
		return Response(text = 'ok')

@routes.post('/get_lvl')
async def get_lvl(request):
	if user_id := await join_key(request):
		await data.lvl.get_lvl(user_id)
		return json_response(data.lvl)

@routes.post('/get_top')
async def get_top(request):
	if user_id := await join_key(request):
		if set(params := await request.json()) == {'x', 'y'}:
			await data.lvl.get_top(params['x'], params['y'])
			return json_response(data.lvl)