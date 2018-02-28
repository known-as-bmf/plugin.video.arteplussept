from collections import OrderedDict
import requests

from addon import PluginInformation

_base_url = 'http://www.arte.tv/hbbtvv2/'
_base_service = 'services/web/index.php/'
_base_headers = {
    'user-agent': PluginInformation.name + '/' + PluginInformation.version
}

_endpoints = {
    'apps': 'conf/apps/apps.json',
    'filters': 'conf/apps/{app}/filters.json',
    'collection': _base_service + 'OPA/v3/videos/collection/ANY/{collection_id}/{lang}',
    'streams': _base_service + 'OPA/v3/streams/{program_id}/{kind}/{lang}'
}


def apps():
    url = _endpoints['apps']
    return _load_json(url).get('apps', {})


def filters(app_name):
    url = _endpoints['filters'].format(app=app_name)
    return _load_json(url)


def teasers(teasers_path, lang):
    url = _base_service + teasers_path + '/' + lang
    return _load_json(url).get('teasers', [])


def collection(collection_id, lang):
    url = _endpoints['collection'].format(
        collection_id=collection_id, lang=lang)
    return _load_json(url).get('videos', [])


def videos(path, lang):
    url = _base_service + path + '/' + lang
    return _load_json(url).get('videos', [])


def streams(kind, program_id, lang):
    url = _endpoints['streams'] .format(
        kind=kind, program_id=program_id, lang=lang)
    return _load_json(url).get('videoStreams', [])


def _load_json(url, params=None, headers=_base_headers):
    r = requests.get(_base_url + url, params=params, headers=headers)
    return r.json(object_pairs_hook=OrderedDict)
