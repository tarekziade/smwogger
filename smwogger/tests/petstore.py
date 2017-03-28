import asyncio
from smwogger import API


async def print_operations():
    async with API('http://petstore.swagger.io/v2/swagger.json') as api:
        print(api.operations)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(print_operations())
finally:
    loop.close()
