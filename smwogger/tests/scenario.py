from smwogger.cli import console


_VARS = {'prod': 'firefox',
         'ver': 43,
         'channel': 'release',
         'dist': 'default',
         'distver': 'default'}


def scenario(api):
    with console('Getting heartbeat'):
        resp = api.getHeartbeat()

    assert resp.status_code == 200

    with console('Playing with the corhorts'):

        vars = {'locale': 'en-US',
                'territory': 'US'}
        vars.update(_VARS)
        resp = api.addUserToCohort(vars=vars)
        vars['cohort'] = 'default'
        resp = api.returnCohortSettings(vars)
