#!/usr/bin/env python

""" define functions here, with their pin names and the pin type.

    each function returns a pair of lists
    (or objects with a __getitem__ function)

    the first list (or object) contains pin name plus type specifications.

    the type is:

    * "-" for an input pin,
    * "+" for an output pin,
    * "*" for an in/out pin

    each function is then added to the pinspec tuple, below, as a ("NAME",
    function) entry.

    different functions may be added multiple times under the same NAME,
    so that complex (or large) functions can be split into one or more
    groups (and placed on different pinbanks).

    eint, pwm and gpio are slightly odd in that instead of a fixed list
    an object is returned with a __getitem__ function that accepts a
    slice object.  in this way the actual generation of the pin name
    is delayed until it is known precisely how many pins are to be
    generated, and that's not known immediately (or it would be if
    every single one of the functions below had a start and end parameter
    added).  see spec.interfaces.PinGen class slice on pingroup

    the second list is the names of pins that are part of an inout bus.
    this list of pins (a ganged group) will need to be changed under
    the control of the function, as a group.  for example: sdmmc's
    D0-D3 pins are in-out, they all change from input to output at
    the same time under the control of the function, therefore there's
    no point having multiple in-out switch/control wires, as the
    sdmmc is never going to do anything other than switch this entire
    bank all at once.  so in this particular example, sdmmc returns:

        (['CMD+', 'CLK+', 'D0*', 'D1*', 'D2*', 'D3*'] # pin names
         ['D0*', 'D1*', 'D2*', 'D3*'])                # ganged bus names
"""


def i2s(suffix, bank):
    return (['MCK+', 'BCK+', 'LRCK+', 'DI-', 'DO+'],
            [])


def emmc(suffix, bank, pincount=8):
    emmcpins = ['CMD+', 'CLK+']
    inout = []
    for i in range(pincount):
        pname = "D%d*" % i
        emmcpins.append(pname)
        inout.append(pname)
    return (emmcpins, inout)


def sdmmc(suffix, bank):
    return emmc(suffix, bank, pincount=4)


def spi(suffix, bank):
    pins = ['CLK*', 'NSS*', 'MOSI*', 'MISO*']
    return (pins, [])


def quadspi(suffix, bank):
    qpins = ['CK*', 'NSS*']
    inout = []
    for i in range(4):
        pname = "IO%d*" % i
        qpins.append(pname)
        inout.append(pname)
    return (qpins, inout)


def i2c(suffix, bank):
    return (['SDA*', 'SCL*'], [])


def jtag(suffix, bank):
    return (['MS+', 'DI-', 'DO+', 'CK+'], [])


def uart(suffix, bank):
    return (['TX+', 'RX-'], [])


def ulpi(suffix, bank):
    ulpipins = ['CK+', 'DIR+', 'STP+', 'NXT+']
    for i in range(8):
        ulpipins.append('D%d*' % i)
    return (ulpipins, [])


def uartfull(suffix, bank):
    return (['TX+', 'RX-', 'CTS-', 'RTS+'],
            [])


def rgbttl(suffix, bank):
    ttlpins = ['CK+', 'DE+', 'HS+', 'VS+']
    for i in range(24):
        ttlpins.append("D%d+" % i)
    return (ttlpins, [])


def rgmii(suffix, bank):
    buspins = []
    for i in range(4):
        buspins.append("ERXD%d-" % i)
    for i in range(4):
        buspins.append("ETXD%d+" % i)
    buspins += ['ERXCK-', 'ERXERR-', 'ERXDV-',
                'EMDC+', 'EMDIO*',
                'ETXEN+', 'ETXCK+', 'ECRS-',
                'ECOL+', 'ETXERR+']
    return (buspins, [])


def flexbus1(suffix, bank):
    buspins = []
    inout = []
    for i in range(8):
        pname = "AD%d*" % i
        buspins.append(pname)
        inout.append(pname)
    for i in range(2):
        buspins.append("CS%d+" % i)
    buspins += ['ALE', 'OE', 'RW', 'TA', 'CLK+',
                'A0', 'A1', 'TS', 'TBST',
                'TSIZ0', 'TSIZ1']
    for i in range(4):
        buspins.append("BWE%d" % i)
    for i in range(2, 6):
        buspins.append("CS%d+" % i)
    return (buspins, inout)


def flexbus2(suffix, bank):
    buspins = []
    for i in range(8, 32):
        buspins.append("AD%d*" % i)
    return (buspins, buspins)


def sdram1(suffix, bank):
    buspins = []
    inout = []
    for i in range(16):
        pname = "SDRDQM%d*" % i
        buspins.append(pname)
        inout.append(pname)
    for i in range(12):
        buspins.append("SDRAD%d+" % i)
    for i in range(8):
        buspins.append("SDRDQ%d+" % i)
    for i in range(3):
        buspins.append("SDRCS%d#+" % i)
    for i in range(2):
        buspins.append("SDRDQ%d+" % i)
    for i in range(2):
        buspins.append("SDRBA%d+" % i)
    buspins += ['SDRCKE+', 'SDRRAS#+', 'SDRCAS#+', 'SDRWE#+',
                'SDRRST+']
    return (buspins, inout)


def sdram2(suffix, bank):
    buspins = []
    inout = []
    for i in range(3, 6):
        buspins.append("SDRCS%d#+" % i)
    for i in range(16, 32):
        pname = "SDRDQM%d*" % i
        buspins.append(pname)
        inout.append(pname)
    return (buspins, inout)


def mcu8080(suffix, bank):
    buspins = []
    inout = []
    for i in range(8):
        pname = "MCUD%d*" % i
        buspins.append(pname)
        inout.append(pname)
    for i in range(8):
        buspins.append("MCUAD%d+" % (i + 8))
    for i in range(6):
        buspins.append("MCUCS%d+" % i)
    for i in range(2):
        buspins.append("MCUNRB%d+" % i)
    buspins += ['MCUCD+', 'MCURD+', 'MCUWR+', 'MCUCLE+', 'MCUALE+',
                'MCURST+']
    return (buspins, inout)


class RangePin(object):
    def __init__(self, suffix, prefix=None):
        self.suffix = suffix
        self.prefix = prefix or ''

    def __getitem__(self, s):
        res = []
        for idx in range(s.start or 0, s.stop or -1, s.step or 1):
            res.append("%s%d%s" % (self.prefix, idx, self.suffix))
        return res


def eint(suffix, bank):
    return (RangePin("*"), [])


def pwm(suffix, bank):
    return (RangePin("+"), [])


def gpio(suffix, bank):
    return (("GPIO%s" % bank, RangePin(prefix=bank, suffix="*")), [])


# list functions by name here

pinspec = (('IIS', i2s),
           ('MMC', emmc),
           ('SD', sdmmc),
           ('SPI', spi),
           ('QSPI', quadspi),
           ('TWI', i2c),
           ('JTAG', jtag),
           ('UART', uart),
           ('UARTQ', uartfull),
           ('LCD', rgbttl),
           ('ULPI', ulpi),
           ('RG', rgmii),
           ('FB', flexbus1),
           ('FB', flexbus2),
           ('SDR', sdram1),
           ('SDR', sdram2),
           ('EINT', eint),
           ('PWM', pwm),
           ('GPIO', gpio),
           )
