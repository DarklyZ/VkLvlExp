from utils import Data as data
from aiohttp.web import json_response, RouteTableDef

routes = RouteTableDef()

@routes.post('/get_lvl')
async def get_lvl(request):
	params = await request.json()
	await data.lvlweb(params['peer_id']).get_lvl(*params['user_ids'])
	return json_response(data.lvlweb)
