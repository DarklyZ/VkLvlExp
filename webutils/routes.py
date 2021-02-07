from utils import Data as data
from aiohttp.web import json_response, RouteTableDef

routes = RouteTableDef()

@routes.post('/get_lvl')
async def get_lvl(peer_id, user_ids):
	await data.lvlweb(peer_id).get_lvl(*user_ids)
	return json_response(data.lvlweb)

@routes.post('/get_top')
async def get_top(peer_id, x, y):
	await data.lvlweb(peer_id).get_top(x, y)
	return json_response(data.lvlweb)