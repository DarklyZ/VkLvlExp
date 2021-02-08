from aiohttp.web import Response
from json.decoder import JSONDecodeError
from os import getenv

def options(json = False, token = False, content_type = None):
	def decorator(coro):
		async def new_coro(request):
			try:
				if (token and request.headers.getone('TOKEN', None) != getenv('TOKEN')):
					return Response(text="Invalid token", status = 403)
				if (request.content_type != content_type):
					return Response(text="Content type must be 'application/json'", status=400)
				if json:
					return await coro(**await request.json())
				return await coro(request)
			except (TypeError, JSONDecodeError) as e:
				return Response(text = str(e), status = 400)
		return new_coro
	return decorator
