from collections import OrderedDict
import requests

from addon import PluginInformation

_base_url = 'http://www.arte.tv/hbbtvv2'
_base_headers = {'user-agent': PluginInformation.name + '/' + PluginInformation.version}

_endpoints = {
  'apps': '/conf/apps/apps.json',
  'filters': '/conf/apps/{app}/filters.json',
  'teasers': '/services/web/index.php/EMAC/teasers/{app}/{lang}'
}

def apps():
  apps = _load_json(_endpoints['apps'])
  return apps.get('apps', {})

def filters(app):
  return _load_json(_endpoints['filters'].format(app=app))

def teasers(app, lang):
  teasers = _load_json(_endpoints['teasers'].format(app=app.lower(), lang=lang.lower()))
  return teasers.get('teasers', {})

def _load_json(url, params=None, headers=_base_headers):
  r = requests.get(_base_url + url, params=params, headers=headers)
  return r.json(object_pairs_hook=OrderedDict)
