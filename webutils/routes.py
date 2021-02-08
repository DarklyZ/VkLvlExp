from utils import Data as data
from aiohttp.web import Response, json_response, RouteTableDef, Request
from .options import options
from os import getenv

routes = RouteTableDef()

@routes.post('/bot')
async def bot(request):
	request = await request.json()
	print(request)
	if (request.get('type') == 'confirmation'):
		return Response(text = getenv('CONFIRM_KEY'))
	await data.bot.router.route(request, data.bot.polling.api)
	return Response(text = 'ok')

@routes.post('/get_lvl')
@options(json = True, secret_key = True, content_type = 'application/json')
async def get_lvl(peer_id, user_ids):
	await data.lvl(peer_id).get_lvl(*user_ids)
	return json_response(data.lvl)

@routes.post('/get_top')
@options(json = True, secret_key = True, content_type = 'application/json')
async def get_top(peer_id, x, y):
	await data.lvl(peer_id).get_top(x, y)
	return json_response(data.lvl)