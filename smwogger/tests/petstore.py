import asyncio
import json
from uuid import uuid4
from smwogger import API


async def print_operations(q):

    name = "tarekounet-%s" % (str(uuid4()))
    data = {}

    def reader(name, value):
        data[name] = value

    async with API('http://petstore.swagger.io/v2/swagger.json', verbose=2,
                   stream=q) as api:
        # let's add a new pet
        pet = {"name": name,
               "photoUrls": ["string"],
               "status": "available"}

        pet = json.dumps(pet)
        headers = {'Content-Type': 'application/json',
                   'api_key': 'special-key'}
        res = await api.addPet(check=False,
                               request={'data': pet, 'headers': headers},
                               response={'vars': {'id': {'query': 'id'}}},
                               data_reader=reader)

        result = await res.json()
        vars = {'petId': data['id']}
        res = await api.getPetById(vars=vars, data_reader=reader,
                                   request={'headers': headers})
        result = await res.json()
        print(result)


loop = asyncio.get_event_loop()
q = asyncio.Queue()

try:
    loop.run_until_complete(print_operations(q))
finally:
    while not q.empty():
        print(q.get_nowait())
    loop.close()
