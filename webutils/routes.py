from utils import Data as data
from aiohttp.web import RouteTableDef, Response, json_response
from . import options
from os import getenv

routes = RouteTableDef()

@routes.post('/bot')
@options(json = True)
async def bot(request, secret, type, group_id, **kwargs):
	if secret != getenv('SECRET_KEY'):
		return Response(text = 'Invalid secret key', status = 403)
	if type == 'confirmation':
		return Response(text = getenv('CONFIRM_KEY'))
	if request.headers.getone('X-Retry-Counter', False):
		return Response(text = 'ok')
	del request

	data.bot.polling.group_id = group_id
	await data.bot.router.route(kwargs | locals(), data.bot.api)
	return Response(text = 'ok')

@routes.post('/get_lvl')
@options(json = True, secret_key = True, user_key = True)
async def get_lvl(request, user_id, user_ids):
	await data.lvl.get_lvl(*user_ids)
	return json_response(data.lvl)

@routes.post('/get_top')
@options(json = True, secret_key = True, user_key = True)
async def get_top(request, user_id, x, y):
	await data.lvl.get_top(x, y)
	return json_response(data.lvl)
