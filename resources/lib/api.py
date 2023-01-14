from collections import OrderedDict
import requests
import xbmc

import hof

from addon import PluginInformation


# Arte hbbtv - deprecated API since 2022 prefer Arte TV API
_base_api_url = 'http://www.arte.tv/hbbtvv2/services/web/index.php'
_base_headers = {
    'user-agent': PluginInformation.name + '/' + PluginInformation.version
}
_endpoints = {
    'categories': '/EMAC/teasers/{type}/v2/{lang}',
    'category': '/EMAC/teasers/category/v2/{category_code}/{lang}',
    'subcategory': '/OPA/v3/videos/subcategory/{sub_category_code}/page/1/limit/100/{lang}',
    'magazines': '/OPA/v3/magazines/{lang}',
    'collection': '/EMAC/teasers/collection/v2/{collection_id}/{lang}',
    # program details
    'video': '/OPA/v3/videos/{program_id}/{lang}',
    # program streams
    'streams': '/OPA/v3/streams/{program_id}/{kind}/{lang}',
    'daily': '/OPA/v3/programs/{date}/{lang}'
}


# Arte TV API - Used on Arte TV website
_artetv_url = 'https://api.arte.tv/api'
_artetv_endpoints = {
    'token': '/sso/v3/token', # POST
    'favorites': '/sso/v3/favorites/{lang}?page={page}&limit={limit}', #GET
    'last_viewed': '/sso/v3/lastvieweds/{lang}?page={page}&limit={limit}', #GET
    'live': '/player/v2/config/{lang}/LIVE', #GET
}
_artetv_headers = {
    'authorization': 'I6k2z58YGO08P1X0E8A7VBOjDxr8Lecg', # required to use token endpoint
    'client': 'web', # required for Arte TV API
    'accept': 'application/json'
}

# Retrieve favorites from a personal account.
def favorites(plugin, lang, usr, pwd):
    url = _artetv_url + _artetv_endpoints['favorites'].format(lang=lang, page='1', limit='50')
    return _load_json_personal_content(plugin, url, usr, pwd)

# Retrieve content recently watched by a user.
def last_viewed(plugin, lang, usr, pwd):
    url = _artetv_url + _artetv_endpoints['last_viewed'].format(lang=lang, page='1', limit='50')
    return _load_json_personal_content(plugin, url, usr, pwd)

def live_video(lang):
    url = _artetv_url + _artetv_endpoints['live'].format(lang=lang)
    return _load_json_full_url(url, None).get('data', {})


def categories(lang):
    url = _endpoints['categories'].format(type='categories', lang=lang)
    return _load_json(url).get('categories', {})


def home_category(name, lang):
    url = _endpoints['categories'].format(type='home', lang=lang)
    return _load_json(url).get('teasers', {}).get(name, [])


def magazines(lang):
    url = _endpoints['magazines'].format(lang=lang)
    return _load_json(url).get('magazines', {})


def category(category_code, lang):
    url = _endpoints['category'].format(category_code=category_code, lang=lang)
    return _load_json(url).get('category', {})


def subcategory(sub_category_code, lang):
    url = _endpoints['subcategory'].format(
        sub_category_code=sub_category_code, lang=lang)
    return _load_json(url).get('videos', {})


def collection(kind, collection_id, lang):
    url = _endpoints['collection'].format(kind=kind,
                                          collection_id=collection_id, lang=lang)
    subCollections = _load_json(url).get('subCollections', [])
    return hof.flat_map(lambda subCollections: subCollections.get('videos', []), subCollections)


def video(program_id, lang):
    url = _endpoints['video'] .format(
        program_id=program_id, lang=lang)
    return _load_json(url).get('videos', [])[0]


def streams(kind, program_id, lang):
    url = _endpoints['streams'] .format(
        kind=kind, program_id=program_id, lang=lang)
    return _load_json(url).get('videoStreams', [])


def daily(date, lang):
    url = _endpoints['daily'].format(date=date, lang=lang)
    return _load_json(url).get('programs', [])

# Deprecated since 2022. Prefer building url on client side
def _load_json(path, headers=_base_headers):
    url = _base_api_url + path
    return _load_json_full_url(url, headers)

def _load_json_full_url(url, headers=_base_headers):
    # https://requests.readthedocs.io/en/latest/
    r = requests.get(url, headers=headers)
    return r.json(object_pairs_hook=OrderedDict)

# Get a bearer token and add it in headers before sending the request
def _load_json_personal_content(plugin, url, usr, pwd, hdrs=_artetv_headers):
    tkn = token(plugin, usr, pwd)
    if not tkn:
        return None
    headers=hdrs.copy()
    headers['authorization'] = tkn['token_type'] + ' ' + tkn['access_token']
    return _load_json_full_url(url, headers).get('data', [])

# Log in user thanks to his/her settings and get a bearer token
# return None if:
#   - any parameter is empty
#     - silenty if both parameters are empty
#     - with a notification if one is not empty
#   - connection to arte tv failed
def token(plugin, username="", password=""):
    # unable to authenticate if either username or password are empty
    if not username and not password:
        return None
    # inform that setings are incomplete
    if not username or not password:
        msg = plugin.addon.getLocalizedString(30020) + " : " + plugin.addon.getLocalizedString(30021)
        plugin.notify(msg=msg, image='warning')
        return None

    url = _artetv_url + _artetv_endpoints['token']
    token_data = {'anonymous_token': None, 'grant_type': 'password', 'username': username, 'password': password}
    try:
        # https://requests.readthedocs.io/en/latest/
        r = requests.post(url, data=token_data, headers=_artetv_headers)
    except requests.exceptions.ConnectionError as err:
        # unable to auth. e.g.
        # HTTPSConnectionPool(host='api.arte.tv', port=443): Max retries exceeded with url: /api/sso/v3/token
        plugin.notify(msg=plugin.addon.getLocalizedString(30020), image='warning')
        xbmc.log('Unable to authenticate to Arte TV : {err_str}'.format(err_str=err))
        return None
    return r.json(object_pairs_hook=OrderedDict)
