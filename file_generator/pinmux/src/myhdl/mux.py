# mux.py

from math import log
from myhdl import *

period = 20  # clk frequency = 50 MHz


@block
def mux4(clk, in_a, in_b, in_c, in_d,
         selector, out):
    sel_r = Signal(intbv(0)[2:0])
    sel25 = Signal(intbv(0)[4:0])

    #@always(clk.posedge, reset_n.negedge)
    # def logic_reg():
    #    if reset_n == 0:
    #        out.next = 0
    #    else:
    #        out.next = count_next

    @always(clk.posedge)
    def logic_selection():
        sel_r.next = selector

    @always(clk.posedge, sel_r)
    def logic_next():
        if selector != sel_r:
            sel25.next = intbv(0)[2:0]
        else:
            if selector == intbv(0)[2:0]:
                sel25.next = intbv(1)[4:0]
            if selector == intbv(1)[2:0]:
                sel25.next = intbv(2)[4:0]
            if selector == intbv(2)[2:0]:
                sel25.next = intbv(4)[4:0]
            if selector == intbv(3)[2:0]:
                sel25.next = intbv(8)[4:0]

    #@always(clk.posedge, clk.negedge)
    @always(sel25, in_a, in_b, in_c, in_d)
    def make_out():
        out.next = bool(in_a if sel25[0] else False) | \
            bool(in_b if sel25[1] else False) | \
            bool(in_c if sel25[2] else False) | \
            bool(in_d if sel25[3] else False)

    return instances()  # return all instances


# testbench
@block
def mux_tb():

    clk = Signal(bool(0))
    in_a = Signal(intbv(0)[1:0])
    in_b = Signal(intbv(0)[1:0])
    in_c = Signal(intbv(0)[1:0])
    in_d = Signal(intbv(0)[1:0])
    selector = Signal(intbv(0)[2:0])
    out = Signal(bool(0))

    mux_inst = mux4(clk, in_a, in_b, in_c, in_d, selector, out)

    @instance
    def clk_signal():
        while True:
            clk.next = not clk
            if clk:
                in_a.next = not in_a
                if in_a:
                    in_b.next = not in_b
                    if in_b:
                        in_c.next = not in_c
                        if in_c:
                            in_d.next = not in_d
                            if in_d:
                                if selector == 3:
                                    selector.next = 0
                                else:
                                    selector.next = selector + 1
            yield delay(period // 2)

    # print simulation data on screen and file
    file_data = open("mux.csv", 'w')  # file for saving data
    # # print header on screen
    s = "{0},{1},{2},{3},{4},{5}".format("in_a", "in_b", "in_c", "in_d",
                                         "selector", "out")
    print(s)
    # # print header to file
    file_data.write(s)
    # print data on each clock

    @always(clk.posedge)
    def print_data():
        # print on screen
        # print.format is not supported in MyHDL 1.0
        print ("%s,%s,%s,%s,%s,%s" %
               (in_a, in_b,
                in_c, in_d,
                selector, out))

        # print in file
        # print.format is not supported in MyHDL 1.0
        #file_data.write(s + "\n")

    return instances()


def main():

    clk = Signal(bool(0))
    in_a = Signal(intbv(0)[1:0])
    in_b = Signal(intbv(0)[1:0])
    in_c = Signal(intbv(0)[1:0])
    in_d = Signal(intbv(0)[1:0])
    selector = Signal(intbv(0)[2:0])
    out = Signal(bool(0))

    mux_v = mux4(clk, in_a, in_b, in_c, in_d, selector, out)
    mux_v.convert(hdl="Verilog", initial_values=True)

    # test bench
    tb = mux_tb()
    tb.convert(hdl="Verilog", initial_values=True)
    # keep following lines below the 'tb.convert' line
    # otherwise error will be reported
    tb.config_sim(trace=True)
    tb.run_sim(66 * period)  # run for 15 clock cycle


if __name__ == '__main__':
    main()
