from utils import Data as data
from aiohttp.web import json_response

async def get_users(request):
	params = await request.json()
	await data.lvl_class(params['peer_id']).send(*params['user_ids'])
	return json_response(data.lvl_class)
