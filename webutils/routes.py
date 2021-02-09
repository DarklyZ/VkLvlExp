from utils import Data as data
from aiohttp.web import RouteTableDef, Response, json_response
from . import options
from os import getenv

routes = RouteTableDef()

@routes.post('/bot')
@options(json = True)
async def bot(secret, type, headers, group_id, **kw):
	if secret != getenv('SECRET_KEY'):
		return Response(text = 'Invalid secret key', status = 403)
	if type == 'confirmation':
		return Response(text = getenv('CONFIRM_KEY'))
	if headers.getone('X-Retry-Counter', False):
		print('Retry!')
		return Response(text = 'ok')

	data.bot.polling.group_id = group_id
	await data.bot.router.route(kw | locals(), data.bot.api)
	return

@routes.post('/get_lvl')
@options(json = True, secret_key = True)
async def get_lvl(peer_id, user_ids, **kw):
	await data.lvl(peer_id).get_lvl(*user_ids)
	return json_response(data.lvl)

@routes.post('/get_top')
@options(json = True, secret_key = True)
async def get_top(peer_id, x, y, **kw):
	await data.lvl(peer_id).get_top(x, y)
	return json_response(data.lvl)