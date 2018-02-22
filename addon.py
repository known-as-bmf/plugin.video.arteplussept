
# coding=utf-8
# -*- coding: utf-8 -*-
#
# plugin.video.arteplussept, Kodi add-on to watch videos from http://www.arte.tv/guide/fr/plus7/
# Copyright (C) 2015  known-as-bmf
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from collections import OrderedDict
from xbmcswift2 import Plugin
from xbmcswift2 import actions
import requests
import os
import urllib2
import time
import datetime


plugin = Plugin()

base_url = 'http://www.arte.tv/hbbtvv2'
base_headers = {'user-agent': plugin.name + '/' + plugin.addon.getAddonInfo('version')}

languages = [
  {'short': 'fr', 'long': 'fr_FR'},
  {'short': 'de', 'long': 'de_DE'},
  {'short': 'en', 'long': 'en_GB'},
  {'short': 'es', 'long': 'es_ES'},
  {'short': 'pl', 'long': 'pl_PL'}
]

# settings
language = languages[plugin.get_setting('lang', int)] or languages[0]

def fetch_main():
  apps = load_json('/conf/apps/apps.json')
  return apps.get('apps', {}).values()

@plugin.route('/')
def index():
  items = [{
    'label': localized_string(item.get('name', 'None')),
    'path': plugin.url_for('listing')
  } for item in fetch_main()]
  return items

@plugin.route('/listing')
def listing():
  pass

# helpers
## dict HOF
def map_dict(mapFn, d):
  """
    mapFn: A function taking two params: value, key
    d: The dict to map
  """
  return {k: mapFn(v, k) for k, v in d.iteritems()}

def filter_dict(filterFn, d):
  """
    filterFn: A function taking two params: value, key MUST return a boolean
    d: The dict to filter
  """
  return {k: v for k, v in d.iteritems() if filterFn(v, k)}

def reject_dict(filterFn, d):
  """
    filterFn: A function taking two params: value, key MUST return a boolean
    d: The dict to filter
  """
  def invert(*args, **kwargs):
    return not filterFn(*args, **kwargs)
  return filter_dict(invert, d)

## requests
def load_json(url, params=None, headers=base_headers):
  r = requests.get(base_url + url, params=params, headers=headers)
  return r.json(object_pairs_hook=OrderedDict)

## various
def get_property(d, path, default=None):
  def walk(sub_d, segment):
    if sub_d is None:
      return None
    return sub_d.get(segment)
  segments = path.split('.')
  return reduce(walk, segments, d) or default

def color_dict_to_hex(color):
  rgb_str_dict = reject_dict(lambda v, k: k == 'a', color)
  rgb_dec_dict = map_dict(lambda v, k: int(v), rgb_str_dict)

  color_str = str(dec_bit_to_padded_hex(int(float(color['a']) * 0xFF)))
  for c in ['r', 'g', 'b']:
    color_str += dec_bit_to_padded_hex(rgb_dec_dict[c])
  return color_str

def dec_bit_to_padded_hex(bit):
  """
    bit: an int between 0x0 and 0xFF
  """
  return '{0:0{1}x}'.format(bit, 2)

def localized_string(lang_dict, default=''):
  return lang_dict.get(language.get('short', 'fr'), default)



# plugin bootstrap
if __name__ == '__main__':
  plugin.run()
