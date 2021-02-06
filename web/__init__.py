from aiohttp.web import (
	Application, Response, middleware, get, post, _run_app
)
from os import getenv
from .test import get_top

@middleware
async def middleware(request, handler):
	if (request.headers.getone("Token") == getenv('TOKEN') and request.content_type == 'application/json'):
		return await handler(request)

app = Application(middlewares = [middleware])
app.add_routes([
	post('/{name}', get_top)
])

async def run_app(*args, **kwargs):
	await _run_app(app, *args, **kwargs)
