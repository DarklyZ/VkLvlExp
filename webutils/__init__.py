from aiohttp.web import Application, _run_app
from .routes import routes
from os import getenv

app = Application()
app.add_routes(routes)

async def run_app(**kwargs):
	await _run_app(app, port = getenv('PORT'), **kwargs)