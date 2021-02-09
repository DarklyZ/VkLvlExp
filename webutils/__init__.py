from aiohttp.web import Response
from json.decoder import JSONDecodeError
from os import getenv

def options(json = False, secret_key = False):
	def decorator(coro):
		async def new_coro(request):
			if secret_key and request.headers.getone('secret', None) != getenv('SECRET_KEY'):
				return Response(text = "Invalid secret key", status = 403)
			if json:
				try: return await coro(headers = request.headers, **await request.json())
				except (TypeError, JSONDecodeError) as e:
					return Response(text = str(e), status = 400)
			return await coro(request)
		return new_coro
	return decorator
