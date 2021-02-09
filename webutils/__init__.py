from aiohttp.web import middleware

@middleware
async def middleware(request, handler):
	try: return await handler(request)
	except: pass