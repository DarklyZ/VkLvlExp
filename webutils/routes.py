from utils import Data as data
from aiohttp.web import Response, json_response, RouteTableDef
from json.decoder import JSONDecodeError

routes = RouteTableDef()

def json_load(coro):
	async def decorator(request):
		try:
			return await coro(**await request.json())
		except (TypeError, JSONDecodeError) as e:
			return Response(text = str(e), status = 400)
	return decorator

@routes.post('/get_lvl')
@json_load
async def get_lvl(peer_id, user_ids):
	await data.lvl(peer_id).get_lvl(*user_ids)
	return json_response(data.lvl)

@routes.post('/get_top')
@json_load
async def get_top(peer_id, x, y):
	await data.lvl(peer_id).get_top(x, y)
	return json_response(data.lvl)