from addon import plugin

import api
import mapper
import utils
import hof

def index_menus():
    return [{
        'label': plugin.get_string(30001),  # broadcasted videos
        'path': plugin.url_for('broadcast')
    }]


def past_week_programs(lang):
    return hof.flatten([api.daily(d, lang) for d in utils.past_week()])


def map_broadcast_item(items):
    relevant_items = [i.get('video') for i in items if i.get('video') is not None]

    mapped_items = [mapper.map_generic_item(item) for item in relevant_items]
    mapped_items.sort(key=lambda item: item['info']['aired'], reverse=True)

    return mapped_items
