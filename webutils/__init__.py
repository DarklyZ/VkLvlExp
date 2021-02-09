from aiohttp.web import middleware
from .routes import routes

@middleware
async def middleware(request, handler):
	try: return await handler(request)
	except: pass