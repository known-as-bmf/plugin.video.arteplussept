from addon import plugin

import hof
import utils

def map_index_item(app_name, app_config):
  return {
    'label': utils.localized_string(app_config.get('name', 'None')),
    'path': plugin.url_for('app', name=app_name)
  }

def map_app_item(app_config):
  item = {'label': utils.localized_string(app_config.get('label', 'None'))}
  app_type = app_config.get('type')
  if(app_type == 'button'):
    teaser = hof.get_property(app_config, 'data.teasers')
    if(teaser is not None):
      item['path'] = plugin.url_for('teasers', name=teaser)
    else:
      item['path'] = plugin.url_for('listing', url=hof.get_property(app_config, 'data.url'))
    return item
