import os.path

try:
    from UserDict import UserDict
except ImportError:
    from collections import UserDict

from bsv.wire_def import generic_io  # special case
from bsv.wire_def import muxwire  # special case


class Pin(object):
    """ pin interface declaration.
        * name is the name of the pin
        * ready, enabled and io all create a (* .... *) prefix
        * action changes it to an "in" if true
    """

    def __init__(self, name,
                 ready=True,
                 enabled=True,
                 io=False,
                 action=False,
                 bitspec=None):
        self.name = name
        self.ready = ready
        self.enabled = enabled
        self.io = io
        self.action = action
        self.bitspec = bitspec if bitspec else 'Bit#(1)'

    def ifacefmt(self, fmtfn=None):
        res = '    '
        status = []
        if self.ready:
            status.append('always_ready')
        if self.enabled:
            status.append('always_enabled')
        if self.io:
            status.append('result="io"')
        if status:
            res += '(*'
            res += ','.join(status)
            res += '*)'
        res += " method "
        if self.io:
            res += "\n                      "
        name = fmtfn(self.name)
        if self.action:
            res += " Action "
            res += name
            res += ' (%s in)' % self.bitspec
        else:
            res += " %s " % self.bitspec
            res += name
        res += ";"
        return res

    def ifacedef(self, fmtoutfn=None, fmtinfn=None, fmtdecfn=None):
        res = '      method '
        if self.action:
            fmtname = fmtinfn(self.name)
            res += "Action  "
            res += fmtdecfn(self.name)
            res += '(%s in);\n' % self.bitspec
            res += '         %s<=in;\n' % fmtname
            res += '      endmethod'
        else:
            fmtname = fmtoutfn(self.name)
            res += "%s=%s;" % (self.name, fmtname)
        return res

    def wirefmt(self, fmtoutfn=None, fmtinfn=None, fmtdecfn=None):
        res = '      Wire#(%s) ' % self.bitspec
        if self.action:
            res += '%s' % fmtinfn(self.name)
        else:
            res += '%s' % fmtoutfn(self.name)
        res += "<-mkDWire(0);"
        return res


class Interface(object):
    """ create an interface from a list of pinspecs.
        each pinspec is a dictionary, see Pin class arguments
        single indicates that there is only one of these, and
        so the name must *not* be extended numerically (see pname)
    """

    def __init__(self, ifacename, pinspecs, ganged=None, single=False):
        self.ifacename = ifacename
        self.ganged = ganged or {}
        self.pins = []
        self.pinspecs = pinspecs
        self.single = single
        for p in pinspecs:
            _p = {}
            _p.update(p)
            if p.get('outen') is True:  # special case, generate 3 pins
                del _p['outen']
                for psuffix in ['out', 'outen', 'in']:
                    _p['name'] = "%s_%s" % (self.pname(p['name']), psuffix)
                    _p['action'] = psuffix != 'in'
                    self.pins.append(Pin(**_p))
            else:
                _p['name'] = self.pname(p['name'])
                self.pins.append(Pin(**_p))

    def getifacetype(self, name):
        for p in self.pinspecs:
            fname = "%s_%s" % (self.ifacename, p['name'])
            #print "search", self.ifacename, name, fname
            if fname == name:
                if p.get('action'):
                    return 'out'
                elif p.get('outen'):
                    return 'inout'
                return 'input'
        return None

    def pname(self, name):
        """ generates the interface spec e.g. flexbus_ale
            if there is only one flexbus interface, or
            sd{0}_cmd if there are several.  string format
            function turns this into sd0_cmd, sd1_cmd as
            appropriate.  single mode stops the numerical extension.
        """
        if self.single:
            return '%s_%s' % (self.ifacename, name)
        return '%s{0}_%s' % (self.ifacename, name)

    def busfmt(self, *args):
        """ this function creates a bus "ganging" system based
            on input from the {interfacename}.txt file.
            only inout pins that are under the control of the
            interface may be "ganged" together.
        """
        if not self.ganged:
            return ''
        #print self.ganged
        res = []
        for (k, pnames) in self.ganged.items():
            name = self.pname('%senable' % k).format(*args)
            decl = 'Bit#(1) %s = 0;' % name
            res.append(decl)
            ganged = []
            for p in self.pinspecs:
                if p['name'] not in pnames:
                    continue
                pname = self.pname(p['name']).format(*args)
                if p.get('outen') is True:
                    outname = self.ifacefmtoutfn(pname)
                    ganged.append("%s_outen" % outname) # match wirefmt
            
            gangedfmt = '{%s} = duplicate(%s);'
            res.append(gangedfmt % (',\n  '.join(ganged), name))
        return '\n'.join(res) + '\n\n'

    def wirefmt(self, *args):
        res = '\n'.join(map(self.wirefmtpin, self.pins)).format(*args)
        res += '\n'
        for p in self.pinspecs:
            name = self.pname(p['name']).format(*args)
            res += "      GenericIOType %s_io = GenericIOType{\n" % name
            params = []
            if p.get('outen') is True:
                outname = self.ifacefmtoutfn(name)
                params.append('outputval:%s_out,' % outname)
                params.append('output_en:%s_outen,' % outname) # match busfmt
                params.append('input_en:~%s_outen,' % outname)
            elif p.get('action'):
                outname = self.ifacefmtoutfn(name)
                params.append('outputval:%s,' % outname)
                params.append('output_en:1,')
                params.append('input_en:0,')
            else:
                params.append('outputval:0,')
                params.append('output_en:0,')
                params.append('input_en:1,')
            params += ['pullup_en:0,', 'pulldown_en:0,',
                       'pushpull_en:0,', 'drivestrength:0,',
                       'opendrain_en:0']
            for param in params:
                res += '                 %s\n' % param
            res += '      };\n'
        return '\n' + res

    def ifacefmt(self, *args):
        res = '\n'.join(map(self.ifacefmtdecpin, self.pins)).format(*args)
        return '\n' + res

    def ifacefmtdecfn(self, name):
        return name

    def ifacefmtdecfn2(self, name):
        return name

    def ifacefmtoutfn(self, name):
        return "wr%s" % name

    def ifacefmtinfn(self, name):
        return "wr%s" % name

    def wirefmtpin(self, pin):
        return pin.wirefmt(self.ifacefmtoutfn, self.ifacefmtinfn,
                           self.ifacefmtdecfn2)

    def ifacefmtdecpin(self, pin):
        return pin.ifacefmt(self.ifacefmtdecfn)

    def ifacefmtpin(self, pin):
        return pin.ifacedef(self.ifacefmtoutfn, self.ifacefmtinfn,
                            self.ifacefmtdecfn2)

    def ifacedef(self, *args):
        res = '\n'.join(map(self.ifacefmtpin, self.pins))
        res = res.format(*args)
        return '\n' + res + '\n'


class MuxInterface(Interface):

    def wirefmt(self, *args):
        return muxwire.format(*args)


class IOInterface(Interface):

    def ifacefmtoutfn(self, name):
        """ for now strip off io{0}_ part """
        return "cell{0}_mux_out"

    def ifacefmtinfn(self, name):
        return "cell{0}_mux_in"

    def wirefmt(self, *args):
        return generic_io.format(*args)


class Interfaces(UserDict):
    """ contains a list of interface definitions
    """

    def __init__(self, pth):
        self.pth = pth
        self.ifacecount = []
        UserDict.__init__(self, {})
        ift = 'interfaces.txt'
        if pth:
            ift = os.path.join(pth, ift)
        with open(ift, 'r') as ifile:
            for ln in ifile.readlines():
                ln = ln.strip()
                ln = ln.split("\t")
                name = ln[0]
                count = int(ln[1])
                spec, ganged = self.read_spec(pth, name)
                iface = Interface(name, spec, ganged, count == 1)
                self.ifaceadd(name, count, iface)

    def getifacetype(self, fname):
        # finds the interface type, e.g sd_d0 returns "inout"
        for iface in self.values():
            typ = iface.getifacetype(fname)
            if typ:
                return typ
        return None

    def ifaceadd(self, name, count, iface, at=None):
        if at is None:
            at = len(self.ifacecount)
        self.ifacecount.insert(at, (name, count))
        self[name] = iface

    def read_spec(self, pth, name):
        spec = []
        ganged = {}
        fname = '%s.txt' % name
        if pth:
            ift = os.path.join(pth, fname)
        with open(ift, 'r') as sfile:
            for ln in sfile.readlines():
                ln = ln.strip()
                ln = ln.split("\t")
                name = ln[0]
                d = {'name': name}
                if ln[1] == 'out':
                    d['action'] = True
                elif ln[1] == 'inout':
                    d['outen'] = True
                    if len(ln) == 3:
                        bus = ln[2] 
                        if not ganged.has_key(bus):
                            ganged[bus] = []
                        ganged[bus].append(name)
                spec.append(d)
        return spec, ganged

    def ifacedef(self, f, *args):
        for (name, count) in self.ifacecount:
            for i in range(count):
                f.write(self.data[name].ifacedef(i))

    def busfmt(self, f, *args):
        f.write("import BUtils::*;\n\n")
        for (name, count) in self.ifacecount:
            for i in range(count):
                bf = self.data[name].busfmt(i)
                f.write(bf)

    def ifacefmt(self, f, *args):
        comment = '''
          // interface declaration between %s-{0} and pinmux'''
        for (name, count) in self.ifacecount:
            for i in range(count):
                c = comment % name.upper()
                f.write(c.format(i))
                f.write(self.data[name].ifacefmt(i))

    def wirefmt(self, f, *args):
        comment = '\n      // following wires capture signals ' \
                  'to IO CELL if %s-{0} is\n' \
                  '      // allotted to it'
        for (name, count) in self.ifacecount:
            for i in range(count):
                c = comment % name
                f.write(c.format(i))
                f.write(self.data[name].wirefmt(i))


# ========= Interface declarations ================ #

mux_interface = MuxInterface('cell', [{'name': 'mux', 'ready': False,
                                       'enabled': False,
                                       'bitspec': '{1}', 'action': True}])

io_interface = IOInterface(
    'io',
    [{'name': 'cell', 'enabled': False, 'bitspec': 'GenericIOType'},
     {'name': 'inputval', 'action': True, 'io': True}, ])

# == Peripheral Interface definitions == #
# these are the interface of the peripherals to the pin mux
# Outputs from the peripherals will be inputs to the pinmux
# module. Hence the change in direction for most pins

# ======================================= #

# basic test
if __name__ == '__main__':

    uartinterface_decl = Interface('uart',
                                   [{'name': 'rx'},
                                    {'name': 'tx', 'action': True},
                                    ])

    twiinterface_decl = Interface('twi',
                                  [{'name': 'sda', 'outen': True},
                                   {'name': 'scl', 'outen': True},
                                   ])

    def _pinmunge(p, sep, repl, dedupe=True):
        """ munges the text so it's easier to compare.
            splits by separator, strips out blanks, re-joins.
        """
        p = p.strip()
        p = p.split(sep)
        if dedupe:
            p = filter(lambda x: x, p)  # filter out blanks
        return repl.join(p)

    def pinmunge(p):
        """ munges the text so it's easier to compare.
        """
        # first join lines by semicolons, strip out returns
        p = p.split(";")
        p = map(lambda x: x.replace('\n', ''), p)
        p = '\n'.join(p)
        # now split first by brackets, then spaces (deduping on spaces)
        p = _pinmunge(p, "(", " ( ", False)
        p = _pinmunge(p, ")", " ) ", False)
        p = _pinmunge(p, " ", " ")
        return p

    def zipcmp(l1, l2):
        l1 = l1.split("\n")
        l2 = l2.split("\n")
        for p1, p2 in zip(l1, l2):
            print (repr(p1))
            print (repr(p2))
            print ()
            assert p1 == p2

    ifaces = Interfaces()

    ifaceuart = ifaces['uart']
    print (ifaceuart.ifacedef(0))
    print (uartinterface_decl.ifacedef(0))
    assert ifaceuart.ifacedef(0) == uartinterface_decl.ifacedef(0)

    ifacetwi = ifaces['twi']
    print (ifacetwi.ifacedef(0))
    print (twiinterface_decl.ifacedef(0))
    assert ifacetwi.ifacedef(0) == twiinterface_decl.ifacedef(0)
