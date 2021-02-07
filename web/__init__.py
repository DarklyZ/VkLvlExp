from aiohttp.web import (
	Application, Response, middleware, get, post, _run_app
)
from os import getenv
from .test import get_users

@middleware
async def middleware(request, handler):
	if (request.headers.getone("TOKEN", None) != getenv('TOKEN')):
		return Response(text = "Invalid token")
	elif (request.content_type != 'application/json'):
		return Response(text = "Content type must be 'application/json'")
	else:
		return await handler(request)

app = Application(middlewares = [middleware])
app.add_routes([
	post('/get_users', get_users)
])

async def run_app(*args, **kwargs):
	await _run_app(app, *args, **kwargs)
