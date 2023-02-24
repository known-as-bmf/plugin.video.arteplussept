
import functools

def find(findFn, l):
    """
      Will return the first item matching the findFn
      findFn: A function taking one param: value. MUST return a boolean
      l: The list to search
    """
    for item in l:
        if findFn(item):
            return item
    return None


def find_dict(findFn, d):
    """
      Will return the first value matching the findFn
      findFn: A function taking two params: value, key. MUST return a boolean
      d: The dict to search
    """
    for k, v in d.items():
        if findFn(v, k):
            return v
    return None


def map_dict(mapFn, d):
    """
      mapFn: A function taking two params: value, key
      d: The dict to map
    """
    return {k: mapFn(v, k) for k, v in d.items()}


def filter_dict(filterFn, d):
    """
      filterFn: A function taking two params: value, key. MUST return a boolean
      d: The dict to filter
    """
    return {k: v for k, v in d.items() if filterFn(v, k)}

def merge_dicts(*args):
    result = {}
    for d in args:
        result.update(d)
    return result

def flat_map(f, lst):
    return [item for list_item in lst for item in f(list_item)]
