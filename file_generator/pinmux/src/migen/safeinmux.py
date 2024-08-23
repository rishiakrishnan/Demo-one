from functools import reduce
from math import log
from migen.fhdl.module import Module
from migen.fhdl.structure import Mux, Signal, Array, Constant, If, Case
from migen.fhdl import verilog
from migen.sim.core import run_simulation


def orop(x1, x2):
    return x1 | x2


class SafeInputMux(Module):
    def __init__(self, inwidth):
        wlog = int(log(inwidth, 2))
        self.inputs = Array()
        for i in range(inwidth):
            self.inputs.append(Signal(1, name_override="input_{}".format(i)))
        self.output = Signal(name_override="output")
        self.selector = Signal(max=inwidth + 1)
        self.io = set(self.inputs) | set([self.output, self.selector])
        sel_r = Signal(max=inwidth + 1)
        sel25 = Signal(max=1 << inwidth)
        zero = Constant(0)
        muxes = []
        for i in range(len(self.inputs)):
            x = Constant(1 << i, inwidth)
            choose = Signal()
            choose.eq(self.selector & x)
            muxes.append(Mux(self.selector & x, self.inputs[i], zero))
        mux = self.output.eq(reduce(orop, muxes))
        self.comb += mux
        self.sync += sel_r.eq(self.selector)

        d = {}
        x = 1
        for i in range(inwidth):
            d[i] = (sel25.eq(x << i),)

        self.sync += If(self.selector != sel_r,
                        sel25.eq(0),
                        ).Else(
                            Case(sel_r, d)
        )


class Blinker(Module):
    def __init__(self, led, maxperiod1, maxperiod2, select):
        self.counter = Signal(max=maxperiod1 + 1)
        self.period1 = Signal(max=maxperiod1 + 1)
        self.period2 = Signal(max=maxperiod2 + 1)
        self.selector = Signal(max=select + 1)
        self.period = Signal(max=maxperiod1 + 1)
        self.comb += self.period.eq(Mux(self.selector,
                                        self.period1, self.period2))
        self.comb += self.period1.eq(maxperiod1)
        self.comb += self.period2.eq(maxperiod2)
        self.sync += If(self.counter == 0,
                        led.eq(~led),
                        self.counter.eq(self.period)
                        ).Else(
                            self.counter.eq(self.counter - 1)
        )
        self.led = led


def tb(dut):
    swap = 0
    for val in [0, 1]:
        for i in range(4):
            yield dut.inputs[i].eq(val)
            for sel in [0, 1, 2, 3]:
                yield dut.selector.eq(sel)
                yield  # run one more clock
                yield
                s = ''
                ins = []
                for x in range(len(dut.inputs)):
                    ins.append((yield dut.inputs[x]))
                for x in range(len(dut.inputs)):
                    s += ("{0} ".format(ins[x]))
                sel = (yield dut.selector)
                out = (yield dut.output)
                yield
                print("{0} out={1} sel={2}".format(s, out, sel))

                print ("%d %d" % (out, ins[sel]))
                #assert out == ins[sel]


if __name__ == '__main__':
    mux = SafeInputMux(4)
    print(verilog.convert(mux, mux.io))

    mux = SafeInputMux(4)
    run_simulation(mux, tb(mux), vcd_name="safeinputmux.vcd")
