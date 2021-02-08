from utils import Data as data
from aiohttp.web import Response, json_response, RouteTableDef, Request
from .options import options
from os import getenv

routes = RouteTableDef()

@routes.post('/bot')
async def bot(request):
	print(await request.text())
	await data.bot.router.route(await request.json(), bot.polling.api)
	return Response(text = 'ok')

@routes.post('/get_lvl')
@options(json = True, token = True, content_type = 'application/json')
async def get_lvl(peer_id, user_ids):
	await data.lvl(peer_id).get_lvl(*user_ids)
	return json_response(data.lvl)

@routes.post('/get_top')
@options(json = True, token = True, content_type = 'application/json')
async def get_top(peer_id, x, y):
	await data.lvl(peer_id).get_top(x, y)
	return json_response(data.lvl)