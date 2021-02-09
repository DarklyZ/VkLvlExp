from utils import Data as data
from aiohttp.web import Response
from json.decoder import JSONDecodeError
from os import getenv

def options(json = False, secret_key = False, user_key = False):
	def decorator(coro):
		async def new_coro(request):
			kwargs = {'request': request}
			if secret_key and request.headers.getone('secret', None) != getenv('SECRET_KEY'):
				return Response(text = "Invalid secret key", status = 403)
			if user_key and (key := request.headers.getone('key', None)):
				kwargs['user_id'] = await data.lvl.join_key(key)
				if kwargs['user_id'] is None:
					return Response(text = "Invalid user key", status = 401)
			elif not key:
				return Response(text="Invalid user key", status = 401)
			if json:
				try: return await coro(**kwargs | await request.json())
				except (TypeError, JSONDecodeError) as e:
					return Response(text = str(e), status = 400)
			return await coro(**kwargs)
		return new_coro
	return decorator
