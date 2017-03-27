from smwogger.cli import console


_VARS = {'prod': 'firefox',
         'ver': 43,
         'channel': 'release',
         'dist': 'default',
         'distver': 'default'}


async def scenario(api):
    with console('Getting heartbeat'):
        resp = await api.getHeartbeat()

    assert resp.status == 200

    with console('Playing with the cohorts'):
        vars = {'locale': 'en-US',
                'territory': 'US'}
        vars.update(_VARS)
        resp = await api.addUserToCohort(vars=vars)
        vars['cohort'] = 'default'
        resp = await api.returnCohortSettings(vars)
