from addon import plugin

import hof
import utils


def map_index_item(app_name, config):
    return {
        'label': utils.localized_string(config.get('name', 'None')),
        'path': plugin.url_for('app', name=app_name)
    }


def map_app_item(app_name, config):
    item = {
        'label': utils.localized_string(config.get('label', 'None'))
    }
    app_type = config.get('type')
    if(app_type == 'button'):
        return _map_app_button(app_name, item, config)
    if(app_type == 'list'):
        return _map_app_list(app_name, item, config)


def _map_app_button(app_name, item, config):
    teaser = hof.get_property(config, 'data.teasers')
    url = hof.get_property(config, 'data.url')
    if(teaser is not None):
        item['path'] = plugin.url_for(
            'teaser', app_name=app_name, teaser=teaser)
    elif(url is not None):
        item['path'] = plugin.url_for('listing', url=url)
    return item


def _map_app_list(app_name, item, config):
    return item


def map_teaser_item(item):
    return {
        'label': utils.format_title_and_subtitle(item.get('title'), item.get('subtitle'))
    }
