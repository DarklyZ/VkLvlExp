from aiohttp.web import Response
from json.decoder import JSONDecodeError
from os import getenv

def options(json = False, secret_key = False, content_type = None):
	def decorator(coro):
		async def new_coro(request):
			if (secret_key and request.headers.getone('SECRET_KEY', None) != getenv('SECRET_KEY')):
				return Response(text="Invalid token", status = 403)
			if (request.content_type != content_type):
				return Response(text=f"Content type must be '{content_type}'", status = 400)
			if json:
				try: return await coro(**await request.json())
				except (TypeError, JSONDecodeError) as e:
					return Response(text=str(e), status=400)
			return await coro(request)
		return new_coro
	return decorator
