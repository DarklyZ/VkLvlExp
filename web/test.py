from utils import Data as data
from aiohttp.web import Response
from json import dumps
from os import getenv

async def get_top(request):
	params = await request.json()
	await data.lvl_class(params['peer_id']).send(*params['user_ids'])
	return Response(body = dumps(data.lvl_class), content_type = request.content_type)