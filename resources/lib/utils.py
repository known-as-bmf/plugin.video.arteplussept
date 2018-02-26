import time
import datetime

from addon import language
import hof

def color_dict_to_hex(color):
  rgb_str_dict = hof.reject_dict(lambda v, k: k == 'a', color)
  rgb_dec_dict = hof.map_dict(lambda v, k: int(v), rgb_str_dict)

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


def parse_date(datestr):
  date = None
  # workaround for datetime.strptime not working (NoneType ???)
  try:
    date = datetime.datetime.strptime(datestr, '%a, %d %b %Y %H:%M:%S')
  except TypeError:
    date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(datestr, '%a, %d %b %Y %H:%M:%S')))
  return date
