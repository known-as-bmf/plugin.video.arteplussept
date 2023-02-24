from addon import PluginInformation
from collections import OrderedDict
import requests
from xbmcswift2 import xbmc
from . import hof


# Arte hbbtv - deprecated API since 2022 prefer Arte TV API
_base_api_url = 'http://www.arte.tv/hbbtvv2/services/web/index.php'
_base_headers = {
    'user-agent': PluginInformation.name + '/' + PluginInformation.version
}
_endpoints = {
    'category': '/EMAC/teasers/category/v2/{category_code}/{lang}',
    'collection': '/EMAC/teasers/collection/v2/{collection_id}/{lang}',
    # program details
    'video': '/OPA/v3/videos/{program_id}/{lang}',
    # program streams
    'streams': '/OPA/v3/streams/{program_id}/{kind}/{lang}',
    'daily': '/OPA/v3/programs/{date}/{lang}'
}


# Arte TV API - Used on Arte TV website
_artetv_url = 'https://api.arte.tv/api'
_artetv_rproxy_url = 'https://arte.tv/api/rproxy'
_artetv_auth_url = 'https://auth.arte.tv/ssologin'
_artetv_endpoints = {
    # POST
    'token': '/sso/v3/token',
    # needs token in authorization header
    'get_favorites': '/sso/v3/favorites/{lang}?page={page}&limit={limit}',
    # PUT
    # needs token in authorization header
    'add_favorite': '/sso/v3/favorites',
    # DELETE
    # needs token in authorization header
    'remove_favorite': '/sso/v3/favorites/{program_id}',
    # needs token in authorization header
    'get_last_viewed': '/sso/v3/lastvieweds/{lang}?page={page}&limit={limit}',
    # PUT
    # needs token in authorization header
    # payload {'programId':'110342-012-A','timecode':574} for 574s i.e. 9:34
    'sync_last_viewed': '/sso/v3/lastvieweds',
    # PATCH empty payload
    # needs token in authorization header
    'purge_last_viewed': '/sso/v3/lastvieweds/purge',
    # program_id can be 103520-000-A or LIVE
    'program': '/player/v2/config/{lang}/{program_id}',
    # rproxy
    # category=HOME, CIN, SER, SEARCH client=app, tv, web, orange, free
    'page': '/emac/v4/{lang}/{client}/pages/{category}/',
    # not yet impl.
    # rproxy date=2023-01-17
    # 'guide_tv': '/emac/v3/{lang}/{client}/pages/TV_GUIDE/?day={DATE}',
    # auth api
    'custom_token': '/setCustomToken',
    # auth api
    'login': '/login',
}
_artetv_headers = {
    'user-agent': PluginInformation.name + '/' + PluginInformation.version,
    # required to use token endpoint
    'authorization': 'I6k2z58YGO08P1X0E8A7VBOjDxr8Lecg',
    # required for Arte TV API. values like web, app, tv, orange, free
    # prefer client tv over web so that Arte adapt content to tv limiting links for instance
    'client': 'tv',
    'accept': 'application/json'
}

# Retrieve favorites from a personal account.
def get_favorites(plugin, lang, usr, pwd):
    url = _artetv_url + _artetv_endpoints['get_favorites'].format(lang=lang, page='1', limit='50')
    return _load_json_personal_content(plugin, url, usr, pwd)

def add_favorite(plugin, usr, pwd, program_id):
    url = _artetv_url + _artetv_endpoints['add_favorite']
    headers = _add_auth_token(plugin, usr, pwd, _artetv_headers)
    data = {'programId': program_id}
    r = requests.put(url, data=data, headers=headers)
    return r.status_code

def remove_favorite(plugin, usr, pwd, program_id):
    url = _artetv_url + _artetv_endpoints['remove_favorite'].format(program_id=program_id)
    headers = _add_auth_token(plugin, usr, pwd, _artetv_headers)
    r = requests.delete(url, headers=headers)
    return r.status_code

# Retrieve content recently watched by a user.
def get_last_viewed(plugin, lang, usr, pwd):
    url = _artetv_url + _artetv_endpoints['get_last_viewed'].format(lang=lang, page='1', limit='50')
    return _load_json_personal_content(plugin, url, usr, pwd)

def sync_last_viewed(plugin, usr, pwd, program_id, time):
    url = _artetv_url + _artetv_endpoints['sync_last_viewed']
    headers = _add_auth_token(plugin, usr, pwd, _artetv_headers)
    data = {'programId': program_id, 'timecode': time}
    r = requests.put(url, data=data, headers=headers)
    return r.status_code

def purge_last_viewed(plugin, usr, pwd):
    url = _artetv_url + _artetv_endpoints['purge_last_viewed']
    headers = _add_auth_token(plugin, usr, pwd, _artetv_headers)
    r = requests.patch(url, data={}, headers=headers)
    return r.status_code

def program_video(lang, program_id):
    url = _artetv_url + _artetv_endpoints['program'].format(lang=lang, program_id=program_id)
    return _load_json_full_url(url, None).get('data', {})


def category(category_code, lang):
    url = _endpoints['category'].format(category_code=category_code, lang=lang)
    return _load_json(url).get('category', {})


def collection(kind, collection_id, lang):
    url = _endpoints['collection'].format(
        kind=kind, collection_id=collection_id, lang=lang)
    subCollections = _load_json(url).get('subCollections', [])
    return hof.flat_map(lambda subCollections: subCollections.get('videos', []), subCollections)


def video(program_id, lang):
    url = _endpoints['video'].format(
        program_id=program_id, lang=lang)
    return _load_json(url).get('videos', [])[0]


def streams(kind, program_id, lang):
    url = _endpoints['streams'].format(
        kind=kind, program_id=program_id, lang=lang)
    return _load_json(url).get('videoStreams', [])


def daily(date, lang):
    url = _endpoints['daily'].format(date=date, lang=lang)
    return _load_json(url).get('programs', [])

# Get content to be display in a page. It can be a page for a category or the home page.
def page(lang):
    url = _artetv_rproxy_url + _artetv_endpoints['page'].format(lang=lang, category='HOME', client='tv')
    return _load_json_full_url(url, _artetv_headers).get('value', [])

# /emac/v4/{lang}/{client}/pages/SEARCH/?page={page}&query={query}
def search(lang, query, page='1'):
    url = _artetv_rproxy_url + _artetv_endpoints['page'].format(lang=lang, category='SEARCH', client='tv')
    params = {'page' : page, 'query' : query}
    return _load_json_full_url(url, _artetv_headers, params).get('value', []).get('zones', [None])[0]

# Deprecated since 2022. Prefer building url on client side
def _load_json(path, headers=_base_headers):
    url = _base_api_url + path
    return _load_json_full_url(url, headers)

def _load_json_full_url(url, headers=_base_headers, params=None):
    # https://requests.readthedocs.io/en/latest/
    r = requests.get(url, headers=headers, params=params)
    return r.json(object_pairs_hook=OrderedDict)

# Get a bearer token and add it in headers before sending the request
def _load_json_personal_content(plugin, url, usr, pwd, hdrs=_artetv_headers):
    headers = _add_auth_token(plugin, usr, pwd, hdrs)
    if not headers:
        return None
    return _load_json_full_url(url, headers).get('data', [])

# Get a bearer token and add it as HTTP header authorization
def _add_auth_token(plugin, usr, pwd, hdrs):
    tkn = get_and_persist_token(plugin, usr, pwd)
    if not tkn:
        return None
    headers = hdrs.copy()
    headers['authorization'] = tkn['token_type'] + ' ' + tkn['access_token']
    # web client needed to reuse token. Otherwise API rejects with 
    # {"error":"invalid_client","error_description":"Client not authorized"}
    headers['client'] = 'web'
    return headers

# Log in user thanks to his/her settings and get a bearer token
# return None if:
#   - any parameter is empty
#     - silenty if both parameters are empty
#     - with a notification if one is not empty
#   - connection to arte tv failed
def get_and_persist_token(plugin, username='', password='', headers=_artetv_headers):
    # unable to authenticate if either username or password are empty
    if not username and not password:
        plugin.notify(msg=plugin.addon.getLocalizedString(30022), image='info')
        return None
    # inform that settings are incomplete
    if not username or not password:
        msg = plugin.addon.getLocalizedString(30020) + ' : ' + plugin.addon.getLocalizedString(30021)
        plugin.notify(msg=msg, image='warning')
        return None

    cached_token = plugin.get_storage('token', TTL=24*60)
    token_idx = '{usr}_{hash}'.format(usr=username, hash=hash(password))
    if token_idx in cached_token:
        xbmc.log('"{usr}" already authenticated to Arte TV : {tkn}'.format(usr=username, tkn=cached_token[token_idx]['access_token']))
        return cached_token[token_idx]

    # set client to web, because with tv get error client_invalid, error Client not authorized
    headers['client'] = 'web'

    tokens = authenticate_in_arte(plugin, username, password, headers)
    # exit if authentication failed
    if not tokens:
        return None
    
    # try to persist token in arte to be allowed to reuse; otherwise token is one-shot
    if persist_token_in_arte(plugin, tokens, headers):
        # token persisted remotly are stored in kodi cache to be reused
        cached_token[token_idx] = tokens
        xbmc.log('"{user}" is successfully authenticated to Arte TV'.format(user=username))
        xbmc.log('Token persisted for a day "{tkn}"'.format(tkn=tokens['access_token']))
    # return persisted or unpersisted token anyway
    return tokens
    

# return None if authentication failed and display an error notification
# return arte reply with access and refresh tokens if authentication was successfull (i.e. status 200, no exception)
def authenticate_in_arte(plugin, username='', password='', headers=_artetv_headers):
    url = _artetv_url + _artetv_endpoints['token']
    token_data = {'anonymous_token': None, 'grant_type': 'password', 'username': username, 'password': password}
    xbmc.log('Try authenticating "{user}" to Arte TV'.format(user=username))
    error = None
    r = None
    try:
        # https://requests.readthedocs.io/en/latest/
        r = requests.post(url, data=token_data, headers=headers)
    except requests.exceptions.ConnectionError as err:
        # unable to auth. e.g.
        # HTTPSConnectionPool(host='api.arte.tv', port=443): Max retries exceeded with url: /api/sso/v3/token
        error = err
    if error or not r or r.status_code != 200:
        plugin.notify(msg=plugin.addon.getLocalizedString(30020), image='error')
        xbmc.log('Unable to authenticate to Arte TV : {err}'.format(err=error if error else r.text))
        return None
    return r.json(object_pairs_hook=OrderedDict)

# calls the sequence of 2 services to be able to reuse authentication token
# return True, if token is persisted, False otherwise. Notify the user with a warning if persistance failed.
def persist_token_in_arte(plugin, tokens, headers):
    # constants taken from my reverse engineering
    api_key = '97598990-f0af-427b-893e-9da348d9f5a6'
    cookies = {'TCPID' : '123261154911117061452', 'TC_PRIVACY' : '1%40031%7C29%7C3445%40%40%401677322453596%2C1677322453596%2C1711018453596%40', 'TC_PRIVACY_CENTER' : None}

    # step 1/2 : get additional cookies for step 2.
    url = _artetv_auth_url + _artetv_endpoints['custom_token']
    params = {'shouldValidateAnonymous' : False, 'token' : tokens['access_token'], 'apikey' : api_key, 'isrememberme' : True}
    error = None
    custom_token = None
    try:
        custom_token = requests.get(url,params=params, headers=headers, cookies=cookies)
    except requests.exceptions.ConnectionError as err:
        error = err
    if error or not custom_token or custom_token.status_code != 200:
        plugin.notify(msg=plugin.addon.getLocalizedString(30020), image='warning')
        xbmc.log('Unable to persist Arte TV token {tkn} for {user}. Step 1/2: {err}'.format(tkn=tokens['access_token'], user=username, err=error if error else custom_token.text))
        return False

    # step 2/2 : persist / remember token so that it can be reused
    url = _artetv_auth_url + _artetv_endpoints['login']
    params = {'shouldValidateAnonymous' : 'false', 'apikey' : api_key}
    cookies = hof.merge_dicts(cookies, custom_token.cookies)
    login = None
    try:
        login = requests.get(url,params=params, headers=headers, cookies=cookies)
    except requests.exceptions.ConnectionError as err:
        error = err
    if error or not login or login.status_code != 200:
        plugin.notify(msg=plugin.addon.getLocalizedString(30020), image='warning')
        xbmc.log('Unable to persist Arte TV token {tkn} for {user}. Step 2/2: {err}'.format(tkn=tokens['access_token'], user=username, err=error if error else login.text))
        return False
    
    return True
