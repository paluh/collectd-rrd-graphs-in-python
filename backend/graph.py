from pyrrd.graph import Graph, GraphPrint, Line as Line

from . import localizable_external as backend

class GraphHrule(object):
    """HRULE:value#color[:legend][:dashes[=on_s[,off_s[,on_s,off_s]...]][:dash-offset=offset]]"""

    def __init__(self, value, color, legend='', dashes='', dash_offset=''):
        self.value = value
        self.color = color
        self.legend = legend#.encode('utf-8')
        self.dashes = dashes
        self.dash_offset = dash_offset

    def __repr__(self):
        return ':'.join(filter(None, ['HRULE', '%s%s' % (self.value, self.color),
                                      self.legend, self.dashes, self.dash_offset]))


class GraphPrint(GraphPrint):

    def __init__(self, vdefObj, format):
        super(GraphPrint, self).__init__(vdefObj, format if isinstance(format, str) else format.encode('utf-8'))


class Line(Line):

    def __init__(self, *args, **kwargs):
        super(Line, self).__init__(*args, **kwargs)
        #if isinstance(self.legend, unicode):
        #self.legend = self.legend.encode('utf-8')

    def __repr__(self):
        '''
        We override this method for preparing the class's data for
        use with RRDTool.
        '''
        main = self.abbr
        if self.width:
            main += unicode(self.width)
        main += u':%s' % self.vname
        if self.color:
            main += self.color
        if self.legend:
            main += u':"%s"' % self.legend
        if self.stack:
            main += u':STACK'
        return main.encode('utf-8')

class Area(Line):

    def __init__(self, width=None, value=None, defObj=None, color=None,
        legend='', stack=False):
        '''
        If a DEF, VDEF, or CDEF object as passed, the vname will
        be automatically extraced from the object and used.
        '''
        super(Area, self).__init__(value=value, defObj=defObj,
            color=color, legend=legend, stack=stack)
        self.abbr = 'AREA'


class Graph(Graph):

    def __init__(self, env, *args, **kwargs):
        self.env = env
        self.units = kwargs.pop('units', 'si')
        self.right_axis = kwargs.pop('right_axis', None)
        kwargs.setdefault('backend', backend)
        super(Graph, self).__init__(*args, **kwargs)

    def write(self, env=None):
        data = self.backend.prepareObject('graph', self)
        return self.backend.graph(*data, env=self.env)
