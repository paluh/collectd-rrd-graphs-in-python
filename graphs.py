import argparse
import calendar
import datetime
import functools
import os
from pyrrd.graph import (CalculationDefinition, ColorAttributes, DataDefinition,
                         VariableDefinition)
import pytz
import time
from backend.graph import Area, Graph, GraphPrint, GraphHrule, Line
from cdef import Average, Last, Maximum, Minimum, Expression

canvas = '#ffffff'
black = '#000000'

full_red = '#ff0000'
full_green = '#00e000'
full_blue = '#0000ff'
full_yellow = '#f0a000'
full_cyan = '#00a0ff'
full_magenta = '#a000ff'
full_gray = '#333333'

half_red = '#f7b7b7'
half_green = '#b7efb7'
half_blue = '#b7b7f7'
half_yellow = '#f3dfb7'
half_cyan = '#b7dff7'
half_magenta = '#dfb7f7'
half_gray = '#888'
half_bluegreen = '#89b3c9'

def utctimestamp(dt):
    return int(calendar.timegm(dt.utctimetuple()))

def ugettext(s):
    return s

def _graph(graph_vars, start, end, locale=None, units_length=8, **kwargs):
    env = dict(os.environ)
    if locale:
        env['LC_ALL'] = locale.encode('utf-8')
    color = ColorAttributes(lefttop_border='#0000', rightbottom_border='#0000',
                            background='#0000')
    kwargs.setdefault('width', 820)
    graph = Graph(env, '-', imgformat='PNG', height=210, start=utctimestamp(start),
                  end=utctimestamp(end), color=color, units_length=units_length, **kwargs)
    graph.data.extend(graph_vars)
    return graph.write(env=env)

def graph_cpu(plugin_dir, start, end, locale=None):
    user_rrdfile = os.path.join(plugin_dir, 'cpu-user.rrd')
    system_rrdfile = os.path.join(plugin_dir, 'cpu-system.rrd')
    wait_rrdfile = os.path.join(plugin_dir, 'cpu-wait.rrd')

    user_min = DataDefinition(rrdfile=user_rrdfile, vname='user_min', dsName='value', cdef='MIN')
    user_avg = DataDefinition(rrdfile=user_rrdfile, vname='user_avg', dsName='value', cdef='AVERAGE')
    user_max = DataDefinition(rrdfile=user_rrdfile, vname='user_max', dsName='value', cdef='MAX')
    user_min_var = VariableDefinition('user_min_var', rpn=unicode(Minimum(Expression(user_min.vname))))
    user_avg_var = VariableDefinition('user_avg_var', rpn=unicode(Average(Expression(user_avg.vname))))
    user_max_var = VariableDefinition('user_max_var', rpn=unicode(Maximum(Expression(user_max.vname))))
    user_last_var = VariableDefinition('user_last_var', rpn=unicode(Last(Expression(user_avg.vname))))

    sys_min = DataDefinition(rrdfile=system_rrdfile, vname='sys_min', dsName='value', cdef='MIN')
    sys_avg = DataDefinition(rrdfile=system_rrdfile, vname='sys_avg', dsName='value', cdef='AVERAGE')
    sys_max = DataDefinition(rrdfile=system_rrdfile, vname='sys_max', dsName='value', cdef='MAX')
    sys_min_var = VariableDefinition('sys_min_var', rpn=unicode(Minimum(Expression(sys_min.vname))))
    sys_avg_var = VariableDefinition('sys_avg_var', rpn=unicode(Average(Expression(sys_avg.vname))))
    sys_max_var = VariableDefinition('sys_max_var', rpn=unicode(Maximum(Expression(sys_max.vname))))
    sys_last_var = VariableDefinition('sys_last_var', rpn=unicode(Last(Expression(sys_avg.vname))))

    wait_min = DataDefinition(rrdfile=wait_rrdfile, vname='wait_min', dsName='value', cdef='MIN')
    wait_avg = DataDefinition(rrdfile=wait_rrdfile, vname='wait_avg', dsName='value', cdef='AVERAGE')
    wait_max = DataDefinition(rrdfile=wait_rrdfile, vname='wait_max', dsName='value', cdef='MAX')
    wait_min_var = VariableDefinition('wait_min_var', rpn=unicode(Minimum(Expression(wait_min.vname))))
    wait_avg_var = VariableDefinition('wait_avg_var', rpn=unicode(Average(Expression(wait_avg.vname))))
    wait_max_var = VariableDefinition('wait_max_var', rpn=unicode(Maximum(Expression(wait_max.vname))))
    wait_last_var = VariableDefinition('wait_last_var', rpn=unicode(Last(Expression(wait_avg.vname))))

    user_sys_avg = CalculationDefinition(vname='user_sys', rpn=unicode(Expression('sys_avg')+Expression('user_avg')))

    graph_vars = [user_min, user_avg, user_max,
                  user_min_var, user_avg_var, user_max_var, user_last_var,
                  sys_min, sys_avg, sys_max, user_sys_avg,
                  sys_min_var, sys_avg_var, sys_max_var, sys_last_var,
                  wait_min, wait_avg, wait_max,
                  wait_min_var, wait_avg_var, wait_max_var, wait_last_var]

    user_label = ugettext('User\:')
    system_label = ugettext('System\:')
    wait_label = ugettext('Wait-IO\:')
    max_ll = max(len(l) for l in [user_label, system_label, wait_label])

    graph_vars.append(Area(defObj=user_sys_avg, color=half_blue))
    graph_vars.append(Line(1, defObj=user_sys_avg, color=full_blue,
                           legend=('%%-%is'% max_ll) % user_label))
    graph_vars.append(GraphPrint(user_min_var, ugettext('%8.1lf Min,')))
    graph_vars.append(GraphPrint(user_avg_var, ugettext('%8.1lf Avg,')))
    graph_vars.append(GraphPrint(user_max_var, ugettext('%8.1lf Max,')))
    graph_vars.append(GraphPrint(user_last_var, ugettext('%8.1lf Last\l')))
    graph_vars.append(Area(defObj=sys_avg, color=half_red))
    graph_vars.append(Line(1, defObj=sys_avg, color=full_red,
                           legend=('%%-%is'% max_ll) % system_label))
    graph_vars.append(GraphPrint(sys_min_var, ugettext('%8.1lf Min,')))
    graph_vars.append(GraphPrint(sys_avg_var, ugettext('%8.1lf Avg,')))
    graph_vars.append(GraphPrint(sys_max_var, ugettext('%8.1lf Max,')))
    graph_vars.append(GraphPrint(sys_last_var, ugettext('%8.1lf Last\l')))
    graph_vars.append(Area(defObj=wait_avg, color=half_yellow))
    graph_vars.append(Line(1, defObj=wait_avg, color=full_yellow,
                           legend=('%%-%is'% max_ll) % wait_label))
    graph_vars.append(GraphPrint(wait_min_var, ugettext('%8.1lf Min,')))
    graph_vars.append(GraphPrint(wait_avg_var, ugettext('%8.1lf Avg,')))
    graph_vars.append(GraphPrint(wait_max_var, ugettext('%8.1lf Max,')))
    graph_vars.append(GraphPrint(wait_last_var, ugettext('%8.1lf Last\l')))
    return _graph(graph_vars, start, end, locale=locale, y_grid='10:5', upper_limit=110,
                  rigid=True, vertical_label=ugettext('"CPU usage [jiffies]"'))

def graph_load(plugin_dir, start, end, locale=None):
    rrdfile = os.path.join(plugin_dir, 'load.rrd')
    graph_vars = []
    shortterm_min = DataDefinition(rrdfile=rrdfile, vname='shortterm_min',
                                   dsName='shortterm', cdef='MIN')
    shortterm_avg = DataDefinition(rrdfile=rrdfile, vname='shortterm_avg',
                                   dsName='shortterm', cdef='AVERAGE')
    shortterm_max = DataDefinition(rrdfile=rrdfile, vname='shortterm_max',
                                   dsName='shortterm', cdef='MAX')
    shortterm_min_var = VariableDefinition('shortterm_min_var', rpn=unicode(Minimum(Expression(shortterm_min.vname))))
    shortterm_avg_var = VariableDefinition('shortterm_avg_var', rpn=unicode(Average(Expression(shortterm_avg.vname))))
    shortterm_max_var = VariableDefinition('shortterm_max_var', rpn=unicode(Maximum(Expression(shortterm_max.vname))))
    shortterm_last_var = VariableDefinition('shortterm_last_var', rpn=unicode(Last(Expression(shortterm_avg.vname))))

    midterm_min = DataDefinition(rrdfile=rrdfile, vname='midterm_min',
                                 dsName='midterm', cdef='MIN')
    midterm_avg = DataDefinition(rrdfile=rrdfile, vname='midterm_avg',
                                   dsName='midterm', cdef='AVERAGE')
    midterm_max = DataDefinition(rrdfile=rrdfile, vname='midterm_max',
                                   dsName='midterm', cdef='MAX')
    midterm_min_var = VariableDefinition('midterm_min_var', rpn=unicode(Minimum(Expression(midterm_min.vname))))
    midterm_avg_var = VariableDefinition('midterm_avg_var', rpn=unicode(Average(Expression(midterm_avg.vname))))
    midterm_max_var = VariableDefinition('midterm_max_var', rpn=unicode(Maximum(Expression(midterm_max.vname))))
    midterm_last_var = VariableDefinition('midterm_last_var', rpn=unicode(Last(Expression(midterm_avg.vname))))

    longterm_min = DataDefinition(rrdfile=rrdfile, vname='longterm_min',
                                 dsName='longterm', cdef='MIN')
    longterm_avg = DataDefinition(rrdfile=rrdfile, vname='longterm_avg',
                                   dsName='longterm', cdef='AVERAGE')
    longterm_max = DataDefinition(rrdfile=rrdfile, vname='longterm_max',
                                   dsName='longterm', cdef='MAX')
    longterm_min_var = VariableDefinition('longterm_min_var', rpn=unicode(Minimum(Expression(longterm_min.vname))))
    longterm_avg_var = VariableDefinition('longterm_avg_var', rpn=unicode(Average(Expression(longterm_avg.vname))))
    longterm_max_var = VariableDefinition('longterm_max_var', rpn=unicode(Maximum(Expression(longterm_max.vname))))
    longterm_last_var = VariableDefinition('longterm_last_var', rpn=unicode(Last(Expression(longterm_avg.vname))))

    # fuck - we have to manually add spacing ;-)
    longterm_label = ugettext('15 minutes average\:')
    midterm_label = ugettext('5 minutes average\:')
    shorterm_label = ugettext('1 minute average\:')
    max_ll = max(len(l) for l in [longterm_label, midterm_label, shorterm_label])

    graph_vars = [shortterm_min, shortterm_avg, shortterm_max,
                  shortterm_min_var, shortterm_avg_var, shortterm_max_var, shortterm_last_var,
                  midterm_min, midterm_avg, midterm_max,
                  midterm_min_var, midterm_avg_var, midterm_max_var, midterm_last_var,
                  longterm_min, longterm_avg, longterm_max,
                  longterm_min_var, longterm_avg_var, longterm_max_var, longterm_last_var,
                  Area(defObj=shortterm_max, color=half_blue),
                  Area(defObj=shortterm_min, color=canvas),
                  Line(1, defObj=longterm_avg, color=full_red,
                       legend=('%%-%is'% max_ll)%longterm_label),
                  GraphPrint(longterm_min_var, ugettext('%8.1lf Min,')),
                  GraphPrint(longterm_avg_var, ugettext('%8.1lf Avg,')),
                  GraphPrint(longterm_max_var, ugettext('%8.1lf Max,')),
                  GraphPrint(longterm_last_var, ugettext('%8.1lf Last\l')),
                  Line(1, defObj=midterm_avg, color=full_green,
                       legend=('%%-%is'% max_ll)%midterm_label),
                  GraphPrint(midterm_min_var, ugettext('%8.1lf Min,')),
                  GraphPrint(midterm_avg_var, ugettext('%8.1lf Avg,')),
                  GraphPrint(midterm_max_var, ugettext('%8.1lf Max,')),
                  GraphPrint(midterm_last_var, ugettext('%8.1lf Last\l')),
                  Line(1, defObj=shortterm_avg, color=full_blue,
                       legend=('%%-%is'% max_ll)%shorterm_label),
                  GraphPrint(shortterm_min_var, ugettext('%8.1lf Min,')),
                  GraphPrint(shortterm_avg_var, ugettext('%8.1lf Avg,')),
                  GraphPrint(shortterm_max_var, ugettext('%8.1lf Max,')),
                  GraphPrint(shortterm_last_var, ugettext('%8.1lf Last\l')),
                  ]
    return _graph(graph_vars, start, end, vertical_label=ugettext('"System load"'), locale=locale)

def graph_memory(plugin_dir, start, end, locale=None):
    used_rrdfile = os.path.join(plugin_dir, 'memory-used.rrd')
    buffered_rrdfile = os.path.join(plugin_dir, 'memory-buffered.rrd')
    cached_rrdfile = os.path.join(plugin_dir, 'memory-cached.rrd')
    free_rrdfile = os.path.join(plugin_dir, 'memory-free.rrd')

    used_min = DataDefinition(rrdfile=used_rrdfile, vname='used_min', dsName='value', cdef='MIN')
    used_avg = DataDefinition(rrdfile=used_rrdfile, vname='used_avg', dsName='value', cdef='AVERAGE')
    used_max = DataDefinition(rrdfile=used_rrdfile, vname='used_max', dsName='value', cdef='MAX')
    used_min_var = VariableDefinition('used_min_var', rpn=unicode(Minimum(Expression(used_min.vname))))
    used_avg_var = VariableDefinition('used_avg_var', rpn=unicode(Average(Expression(used_avg.vname))))
    used_max_var = VariableDefinition('used_max_var', rpn=unicode(Maximum(Expression(used_max.vname))))
    used_last_var = VariableDefinition('used_last_var', rpn=unicode(Last(Expression(used_avg.vname))))

    buffered_min = DataDefinition(rrdfile=buffered_rrdfile, vname='buffered_min', dsName='value', cdef='MIN')
    buffered_avg = DataDefinition(rrdfile=buffered_rrdfile, vname='buffered_avg', dsName='value', cdef='AVERAGE')
    buffered_max = DataDefinition(rrdfile=buffered_rrdfile, vname='buffered_max', dsName='value', cdef='MAX')
    buffered_min_var = VariableDefinition('buffered_min_var', rpn=unicode(Minimum(Expression(buffered_min.vname))))
    buffered_avg_var = VariableDefinition('buffered_avg_var', rpn=unicode(Average(Expression(buffered_avg.vname))))
    buffered_max_var = VariableDefinition('buffered_max_var', rpn=unicode(Maximum(Expression(buffered_max.vname))))
    buffered_last_var = VariableDefinition('buffered_last_var', rpn=unicode(Last(Expression(buffered_avg.vname))))

    used_with_buffered_max = CalculationDefinition(vname='used_with_buffered_max',
                                                  rpn=unicode(Expression(used_max.vname)+Expression(buffered_max.vname)))

    cached_min = DataDefinition(rrdfile=cached_rrdfile, vname='cached_min', dsName='value', cdef='MIN')
    cached_avg = DataDefinition(rrdfile=cached_rrdfile, vname='cached_avg', dsName='value', cdef='AVERAGE')
    cached_max = DataDefinition(rrdfile=cached_rrdfile, vname='cached_max', dsName='value', cdef='MAX')
    cached_min_var = VariableDefinition('cached_min_var', rpn=unicode(Minimum(Expression(cached_min.vname))))
    cached_avg_var = VariableDefinition('cached_avg_var', rpn=unicode(Average(Expression(cached_avg.vname))))
    cached_max_var = VariableDefinition('cached_max_var', rpn=unicode(Maximum(Expression(cached_max.vname))))
    cached_last_var = VariableDefinition('cached_last_var', rpn=unicode(Last(Expression(cached_avg.vname))))

    used_with_buffered_with_cached_max = CalculationDefinition(vname='used_with_buffered_with_cached_max',
                                                               rpn=unicode(Expression(used_max.vname)+Expression(buffered_max.vname)+Expression(cached_max.vname)))

    free_min = DataDefinition(rrdfile=free_rrdfile, vname='free_min', dsName='value', cdef='MIN')
    free_avg = DataDefinition(rrdfile=free_rrdfile, vname='free_avg', dsName='value', cdef='AVERAGE')
    free_max = DataDefinition(rrdfile=free_rrdfile, vname='free_max', dsName='value', cdef='MAX')
    free_min_var = VariableDefinition('free_min_var', rpn=unicode(Minimum(Expression(free_min.vname))))
    free_avg_var = VariableDefinition('free_avg_var', rpn=unicode(Average(Expression(free_avg.vname))))
    free_max_var = VariableDefinition('free_max_var', rpn=unicode(Maximum(Expression(free_max.vname))))
    free_last_var = VariableDefinition('free_last_var', rpn=unicode(Last(Expression(free_avg.vname))))

    used_with_buffered_with_cached_with_free_max = CalculationDefinition(vname='used_with_buffered_with_cached_with_free_max',
                                                                         rpn=unicode(Expression(used_max.vname) +
                                                                                     Expression(buffered_max.vname) +
                                                                                     Expression(cached_max.vname) +
                                                                                     Expression(free_max.vname)))

    graph_vars = [used_min, used_avg, used_max,
                  used_min_var, used_avg_var, used_max_var, used_last_var,
                  buffered_min, buffered_avg, buffered_max, used_with_buffered_max,
                  buffered_min_var, buffered_avg_var, buffered_max_var, buffered_last_var,
                  cached_min, cached_avg, cached_max, used_with_buffered_with_cached_max,
                  cached_min_var, cached_avg_var, cached_max_var, cached_last_var,
                  free_min, free_avg, free_max, used_with_buffered_with_cached_with_free_max,
                  free_min_var, free_avg_var, free_max_var, free_last_var]

    free_label = ugettext('Free\:')
    page_cache_label = ugettext('Page cache\:')
    buffer_cache_label = ugettext('Buffer cache\:')
    used_label = ugettext('Used\:')
    max_ll = max(len(l) for l in [free_label, page_cache_label, buffer_cache_label, used_label])

    graph_vars.append(Area(defObj=used_with_buffered_with_cached_with_free_max, color=half_green))
    graph_vars.append(Line(1, defObj=used_with_buffered_with_cached_with_free_max, color=full_green,
                           legend=('%%-%is'% max_ll)%free_label))
    graph_vars.append(GraphPrint(free_min_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(free_avg_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(free_max_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(free_last_var, ugettext('%8.1lf%S Last\l')))

    graph_vars.append(Area(defObj=used_with_buffered_with_cached_max, color=half_blue))
    graph_vars.append(Line(1, defObj=used_with_buffered_with_cached_max, color=full_blue,
                           legend=('%%-%is'% max_ll)%page_cache_label))
    graph_vars.append(GraphPrint(cached_min_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(cached_avg_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(cached_max_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(cached_last_var, ugettext('%8.1lf%S Last\l')))

    graph_vars.append(Area(defObj=used_with_buffered_max, color=half_yellow))
    graph_vars.append(Line(1, defObj=used_with_buffered_max, color=full_yellow,
                           legend=('%%-%is'% max_ll)%buffer_cache_label))
    graph_vars.append(GraphPrint(buffered_min_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(buffered_avg_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(buffered_max_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(buffered_last_var, ugettext('%8.1lf%S Last\l')))

    graph_vars.append(Area(defObj=used_max, color=half_red))
    graph_vars.append(Line(1, defObj=used_max, color=full_red,
                           legend=('%%-%is'% max_ll)%used_label))
    graph_vars.append(GraphPrint(used_min_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(used_avg_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(used_max_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(used_last_var, ugettext('%8.1lf%S Last\l')))

    return _graph(graph_vars, start, end, units_exponent=9,
                  vertical_label=ugettext('"Memory usage [Gigabytes]"'),
                  locale=locale)

def graph_interface(plugin_dir, start, end, locale=None, logarithmic=True):
    octets_rrdfile = os.path.join(plugin_dir, 'if_octets.rrd')
    #errors_rrdfile = os.path.join(plugin_dir, 'if_errors.rrd')

    tx_min = DataDefinition(rrdfile=octets_rrdfile, vname='tx_min', dsName='tx', cdef='MIN')
    tx_avg = DataDefinition(rrdfile=octets_rrdfile, vname='tx_avg', dsName='tx', cdef='AVERAGE')
    tx_max = DataDefinition(rrdfile=octets_rrdfile, vname='tx_max', dsName='tx', cdef='MAX')

    # expres traffic in megabits/sec (1e6 bits)
    tx_min_bits = CalculationDefinition(vname='tx_min_bits', rpn=unicode(Expression(tx_min.vname)*8))
    tx_avg_bits = CalculationDefinition(vname='tx_avg_bits', rpn=unicode(Expression(tx_avg.vname)*8))
    tx_max_bits = CalculationDefinition(vname='tx_max_bits', rpn=unicode(Expression(tx_max.vname)*8))

    tx_avg_bits_neg = CalculationDefinition('tx_avg_bits_neg', rpn=unicode(Expression(-1)*Expression(tx_avg_bits.vname)))
    tx_max_bits_neg = CalculationDefinition('tx_max_bits_neg', rpn=unicode(Expression(-1)*Expression(tx_max_bits.vname)))

    tx_min_bits_var = VariableDefinition('tx_min_bits_var', rpn=unicode(Minimum(Expression(tx_min_bits.vname))))
    tx_avg_bits_var = VariableDefinition('tx_avg_bits_var', rpn=unicode(Average(Expression(tx_avg_bits.vname))))
    tx_max_bits_var = VariableDefinition('tx_max_bits_var', rpn=unicode(Maximum(Expression(tx_max_bits.vname))))
    tx_last_bits_var = VariableDefinition('tx_last_bits_var', rpn=unicode(Last(Expression(tx_avg_bits.vname))))

    rx_min = DataDefinition(rrdfile=octets_rrdfile, vname='rx_min', dsName='rx', cdef='MIN')
    rx_avg = DataDefinition(rrdfile=octets_rrdfile, vname='rx_avg', dsName='rx', cdef='AVERAGE')
    rx_max = DataDefinition(rrdfile=octets_rrdfile, vname='rx_max', dsName='rx', cdef='MAX')

    rx_min_bits = CalculationDefinition(vname='rx_min_bits', rpn=unicode(Expression(rx_min.vname)*8))
    rx_avg_bits = CalculationDefinition(vname='rx_avg_bits', rpn=unicode(Expression(rx_avg.vname)*8))
    rx_max_bits = CalculationDefinition(vname='rx_max_bits', rpn=unicode(Expression(rx_max.vname)*8))

    rx_min_bits_var = VariableDefinition('rx_min_bits_var', rpn=unicode(Minimum(Expression(rx_min_bits.vname))))
    rx_avg_bits_var = VariableDefinition('rx_avg_bits_var', rpn=unicode(Average(Expression(rx_avg_bits.vname))))
    rx_max_bits_var = VariableDefinition('rx_max_bits_var', rpn=unicode(Maximum(Expression(rx_max_bits.vname))))
    rx_last_bits_var = VariableDefinition('rx_last_bits_var', rpn=unicode(Last(Expression(rx_avg_bits.vname))))

    graph_vars = [tx_min, tx_avg, tx_max, tx_min_bits, tx_avg_bits, tx_max_bits,
                  tx_avg_bits_neg, tx_max_bits_neg,
                  tx_min_bits_var, tx_avg_bits_var, tx_max_bits_var, tx_last_bits_var,
                  rx_min, rx_avg, rx_max, rx_min_bits, rx_avg_bits, rx_max_bits,
                  rx_min_bits_var, rx_avg_bits_var, rx_max_bits_var, rx_last_bits_var]
    outgoing_label=ugettext('Outgoing\:')
    incoming_label=ugettext('Incoming\:')
    max_ll = max(len(l) for l in [outgoing_label, incoming_label])

    if logarithmic:
        graph_vars.append(Line(1, defObj=rx_max_bits, color=full_green,
                               legend=('%%-%is'% max_ll)%incoming_label))
    else:
        graph_vars.append(Area(defObj=rx_max_bits, color=full_green,
                               legend=('%%-%is'% max_ll)%incoming_label))
    graph_vars.append(GraphPrint(rx_min_bits_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(rx_avg_bits_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(rx_max_bits_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(rx_last_bits_var, ugettext('%8.1lf%S Last\l')))
    if logarithmic:
        graph_vars.append(Line(1, defObj=tx_max_bits, color=full_blue,
                               legend=('%%-%is'% max_ll)%outgoing_label))
    else:
        graph_vars.append(Area(defObj=tx_max_bits_neg, color=full_blue,
                               legend=('%%-%is'% max_ll)%outgoing_label))
    graph_vars.append(GraphPrint(tx_min_bits_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(tx_avg_bits_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(tx_max_bits_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(tx_last_bits_var, ugettext('%8.1lf%S Last\l')))
    graph_vars.append(GraphHrule(0, half_red))
    return _graph(graph_vars, start, end, locale=locale,
                  vertical_label=ugettext('"Network traffic [bits/sec]"'),
                  logarithmic=logarithmic, units='si')

def graph_disk(plugin_dir, start, end, locale=None, logarithmic=True):
    octets_rrdfile = os.path.join(plugin_dir, 'disk_octets.rrd')
    #operations_rrdfile = os.path.join(plugin_dir, 'disk_ops.rrd')

    read_min = DataDefinition(rrdfile=octets_rrdfile, vname='read_min', dsName='read', cdef='MIN')
    read_avg = DataDefinition(rrdfile=octets_rrdfile, vname='read_avg', dsName='read', cdef='AVERAGE')
    read_max = DataDefinition(rrdfile=octets_rrdfile, vname='read_max', dsName='read', cdef='MAX')

    read_min_var = VariableDefinition('read_min_var', rpn=unicode(Minimum(Expression(read_min.vname))))
    read_avg_var = VariableDefinition('read_avg_var', rpn=unicode(Average(Expression(read_avg.vname))))
    read_max_var = VariableDefinition('read_max_var', rpn=unicode(Maximum(Expression(read_max.vname))))
    read_last_var = VariableDefinition('read_last_var', rpn=unicode(Last(Expression(read_avg.vname))))

    write_min = DataDefinition(rrdfile=octets_rrdfile, vname='write_min', dsName='write', cdef='MIN')
    write_avg = DataDefinition(rrdfile=octets_rrdfile, vname='write_avg', dsName='write', cdef='AVERAGE')
    write_max = DataDefinition(rrdfile=octets_rrdfile, vname='write_max', dsName='write', cdef='MAX')

    write_min_var = VariableDefinition('write_min_var', rpn=unicode(Minimum(Expression(write_min.vname))))
    write_avg_var = VariableDefinition('write_avg_var', rpn=unicode(Average(Expression(write_avg.vname))))
    write_max_var = VariableDefinition('write_max_var', rpn=unicode(Maximum(Expression(write_max.vname))))
    write_last_var = VariableDefinition('write_last_var', rpn=unicode(Last(Expression(write_avg.vname))))

    read_max_neg = CalculationDefinition('write_max_neg', rpn=unicode(Expression(-1)*Expression(read_max.vname)))

    graph_vars = [read_min, read_avg, read_max, read_max_neg,
                  write_min, write_avg, write_max,
                  write_min_var, write_avg_var, write_max_var, write_last_var,
                  read_min_var, read_avg_var, read_max_var, read_last_var,
                  ]
    written_label = ugettext('Written\:')
    read_label = ugettext('Read\:')
    max_ll = max(len(l) for l in [read_label, written_label])

    if not logarithmic:
        graph_vars.append(Area(defObj=write_max, color=full_magenta,
                               legend=('%%-%is'% max_ll)%written_label))
    else:
        graph_vars.append(Line(1, defObj=write_max, color=full_magenta,
                               legend=('%%-%is'% max_ll)%written_label))
    graph_vars.append(GraphPrint(write_max_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(write_avg_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(write_min_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(write_last_var, ugettext('%8.1lf%S Last\l')))
    if not logarithmic:
        graph_vars.append(Area(defObj=read_max_neg, color=full_cyan,
                               legend=('%%-%is'% max_ll)%read_label))
    else:
        graph_vars.append(Line(1, defObj=read_max, color=full_cyan,
                               legend=('%%-%is'% max_ll)%read_label))
    graph_vars.append(GraphPrint(read_max_var, ugettext('%8.1lf%S Min,')))
    graph_vars.append(GraphPrint(read_avg_var, ugettext('%8.1lf%S Avg,')))
    graph_vars.append(GraphPrint(read_min_var, ugettext('%8.1lf%S Max,')))
    graph_vars.append(GraphPrint(read_last_var, ugettext('%8.1lf%S Last\l')))
    graph_vars.append(GraphHrule(0, half_red))
    return _graph(graph_vars, start, end, logarithmic=logarithmic, units='si',
                  vertical_label=ugettext('"Disk traffic [bytes/sec]"'),
                  locale=locale)

p2g = {
    'cpu': graph_cpu,
    'load': graph_load,
    'interface': graph_interface,
    'memory': graph_memory,
    'disk': graph_disk,
}

def graph(plugin, rrd_dir, start, end, **kwargs):
    return p2g[plugin](rrd_dir, start, end, **kwargs)

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers()
    name2parser = {}
    datefield_help = 'format Y-m-d - for example: 2013-08-29'
    coerce_date_value = lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date()

    def do_graph(plugin, args):
        timezone = args.timezone if args.timezone is not None else time.tzname[0]
        tzinfo = pytz.timezone(timezone)
        end = datetime.date.today() if args.end is None else args.end
        start = end - datetime.timedelta(days=7) if args.start is None else args.start
        print start
        print end
        start = datetime.datetime.combine(start, datetime.time()).replace(tzinfo=tzinfo)
        end = datetime.datetime.combine(end, datetime.time()).replace(tzinfo=tzinfo)
        if hasattr(args, 'logarithmic'):
            p = graph(plugin, args.rrd_dir, start=start, end=end,
                      locale=args.locale, logarithmic=args.logarithmic)
        else:
            p = graph(plugin, args.rrd_dir, start=start, end=end, locale=args.locale)
        output = args.output if args.output is not None else '%s.png' % plugin
        with open(output, 'w+') as graph_file:
            graph_file.write(p)

    for plugin in ['cpu', 'load', 'interface', 'memory', 'disk']:
        parser = subparsers.add_parser(plugin)
        parser.add_argument('-l', '--locale')
        parser.add_argument('-t', '--timezone')
        parser.add_argument('-s', '--start', help=datefield_help, type=coerce_date_value)
        parser.add_argument('-e', '--end', help=datefield_help, type=coerce_date_value)
        parser.add_argument('-d', '--rrd-dir', required=True)
        parser.add_argument('-o', '--output')
        parser.set_defaults(func=functools.partial(do_graph, plugin=plugin))
        name2parser[plugin] = parser

    for name in ['disk', 'interface']:
        name2parser[name].add_argument('--logarithmic', action='store_true', default=False)

    args = main_parser.parse_args()
    args.func(args=args)
