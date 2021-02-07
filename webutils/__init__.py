from aiohttp.web import Application, Response, middleware, _run_app
from .routes import routes
from os import getenv

@middleware
async def middleware(request, handler):
	if (request.headers.getone('TOKEN', None) != getenv('TOKEN')):
		return Response(text = "Invalid token")
	elif (request.content_type != 'application/json'):
		return Response(text = "Content type must be 'application/json'")
	else:
		return await handler(request)

app = Application(middlewares = [middleware])
app.add_routes(routes)

async def run_app(**kwargs):
	await _run_app(app, **kwargs)