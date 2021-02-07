from aiohttp.web import Application, json_response, middleware, _run_app
from json.decoder import JSONDecodeError
from .routes import routes
from os import getenv

def is_custom(handler):
	return handler.__module__ == 'webutils.routes'

@middleware
async def middleware(request, handler):
	if (request.headers.getone('TOKEN', None) != getenv('TOKEN')):
		return json_response({'error': "Invalid token"}, status = 403)
	elif (request.content_type != 'application/json'):
		return json_response({'error': "Content type must be 'application/json'"}, status = 400)
	try: return await handler(**await request.json()) if is_custom(handler) else await handler(request)
	except (TypeError, JSONDecodeError) as e: return json_response({'error': str(e)}, status = 400)

app = Application(middlewares = [middleware])
app.add_routes(routes)

async def run_app(**kwargs):
	await _run_app(app, **kwargs)