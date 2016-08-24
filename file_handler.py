'''for sending and retrieving main info to file'''

#numpy python2 uses cPickle and numpy in python3 uses pickle
from sys import version_info
if version_info[0] > 2:
    from pickle import UnpicklingError
else:
    from cPickle import UnpicklingError


import dicetables as dt
import numpy as np

def _check_dictionary(plot_obj):
    '''checks to make sure that plot object is a dictionary with all appropriate
    keys. returns 'error: <details>' or 'ok'.'''
    expected = {'y_range':tuple, 'x_range': tuple, 'text':str,
                'tuple_list':list, 'pts':list, 'dice':list}
    if not isinstance(plot_obj, dict):
        return 'error: not a dict'
    try:
        for key, val_type in expected.items():
            if not isinstance(plot_obj[key], val_type):
                return 'error: {} not {}'.format(key, val_type)
        return 'ok'
    except KeyError:
        return 'error: missing key'

def is_long(num):
    '''workaround so python2 tests ints and longs and python3 tests ints'''
    try:
        return isinstance(num, (int, long))
    except NameError:
        return isinstance(num, int)

def _check_values(plot_obj):
    '''checks all the values are the right kinds.  returns 'error:<details>'
    or 'ok'.'''
    msg = 'error:'
    msg += check_x_range_are_longs_maybe_return_error_msg(plot_obj)
    msg += check_y_range_are_floats_maybe_return_error_msg(plot_obj)
    msg += check_tuple_list_feq_and_val_are_longs_maybe_return_error_msg(plot_obj)
    msg += check_pts(plot_obj)
    msg += check_dice_list(plot_obj)
    if msg == 'error:':
        msg = 'ok'
    return msg

def flatten_tuple_list(tuple_list):
    output = []
    for a_tuple in tuple_list:
        output.extend(list(a_tuple))
    return output

def check_tuple_list_feq_and_val_are_longs_maybe_return_error_msg(plot_obj):
    msg = ''
    tuples_list_as_list = flatten_tuple_list(plot_obj['tuple_list'])
    if not check_all_numbers_are_longs(tuples_list_as_list):
        msg += ' corrupted "tuple_list"'
    return msg

def check_pts(plot_obj):
    plot_pts = flatten_tuple_list(plot_obj['pts'])
    if not check_all_numbers_are_floats_or_ints(plot_pts):
        return ' corrupted "pts"'
    return ''

def check_pts_old(plot_obj):
    msg = ''
    for tuple_ in plot_obj['pts']:
        for val in tuple_:
            if not isinstance(val, (int, float)):
                msg += ' corrupted "pts"'
    return msg

def check_dice_list(plot_obj):
    msg = ''
    for die, num in plot_obj['dice']:
        if not isinstance(die, dt.ProtoDie) or not isinstance(num, int):
            msg += ' dicelist at ({!r}, {})'.format(die, num)
    return msg

def check_x_range_are_longs_maybe_return_error_msg(plot_obj):
    x_range = plot_obj['x_range']
    if not check_all_numbers_are_longs(x_range):
        return ' incorrect x_range'
    return ''

def check_y_range_are_floats_maybe_return_error_msg(plot_obj):
    y_range = plot_obj['y_range']
    if not check_all_numbers_are_floats(y_range)
        return ' incorrect y_range'
    return ''

def check_all_numbers_are_longs(numbers):
    all_longs = True
    for number in numbers:
        all_longs = all_longs and is_long(number)
    return all_longs
 
def check_all_numbers_are_floats(numbers):
    all_floats = True
    for number in numbers:
        all_floats = all_floats and isinstance(number, float) 
    return all_floats

########=====###

def check_data(plot_obj):
    '''checks history to see if plot_obj has expected data.  if ok, returns 'ok'
    else returns a msg starting with 'error:' '''
    msg = _check_dictionary(plot_obj)
    if msg == 'ok':
        msg = _check_values(plot_obj)
    return msg

def check_history(history):
    '''checks a history(a non-empty iterable containing plot_objects. to make
    sure it has the correct kind of data. if ok, returns 'ok' else returns a msg
    starting with 'error' '''
    for plot_obj in history:
        msg = check_data(plot_obj)
        if 'error:' in msg:
            break
    return msg

def write_history_np(history):
    '''takes a numpy array and writes it'''
    np.save('numpy_history', history)

def read_history_np():
    '''tries to find the np file and read it returns a np array and a message'''
    empty_hist = np.array([], dtype=object)
    try:
        history = np.load('numpy_history.npy')
        if history.size:
            msg = check_history(history)
            if 'error:' in msg:
                history = empty_hist
        else:
            if history.dtype != np.dtype('O'):
                msg = 'error: wrong array type'
                history = empty_hist
            else:
                msg = 'ok: no history'
    except IOError:
        history = empty_hist
        msg = 'error: no file'
    except (UnpicklingError, AttributeError, EOFError, ImportError,
            IndexError, ValueError):
        history = empty_hist
        msg = 'error: file corrupted'
    return msg, history

