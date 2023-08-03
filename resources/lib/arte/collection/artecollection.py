from resources.lib.arte.item import arteitem as ai


class ArteCollection:

    def __init__(self, json_dict):
        self.pages = json_dict.get('data', [])
        self.meta = json_dict.get('meta', None)

    def to_menu(self, plugin, collection_type):
        items = [ai.ArteItem(item).map_artetv_item() for item in self.pages]
        if self.meta and self.meta.get('pages', False):
            total_pages = self.meta.get('pages')
            current_page = self.meta.get('page')
            if current_page > 1:
                # add previous page at the begining
                items.insert(0, {
                    'label': plugin.addon.getLocalizedString(30039),
                    'path': plugin.url_for(collection_type, page=(current_page-1)),
                })
            if current_page < total_pages:
                # add next page at the end
                items.append({
                    'label': plugin.addon.getLocalizedString(30038),
                    'path': plugin.url_for(collection_type, page=(current_page+1)),
                })
        return items
