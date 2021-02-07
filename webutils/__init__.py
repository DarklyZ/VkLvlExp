from aiohttp.web import Application, json_response, middleware, _run_app
from json.decoder import JSONDecodeError
from .routes import routes
from os import getenv

def in_routes(handler):
	return handler.__module__ == 'webutils.routes'

@middleware
async def middleware(request, handler):
	if (request.headers.getone('TOKEN', None) != getenv('TOKEN')):
		return json_response({'error': "Invalid token"})
	elif (request.content_type != 'application/json'):
		return json_response({'error': "Content type must be 'application/json'"})
	else:
		try: return await handler(**await request.json()) if in_routes(handler) else await handler(request)
		except (TypeError, JSONDecodeError) as e: return json_response({'error': str(e)})

app = Application(middlewares = [middleware])
app.add_routes(routes)

async def run_app(**kwargs):
	await _run_app(app, **kwargs)