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

def get_property(d, path, default=None):
  def walk(sub_d, segment):
    if sub_d is None:
      return None
    return sub_d.get(segment)
  segments = path.split('.')
  return reduce(walk, segments, d) or default