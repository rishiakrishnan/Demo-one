
axi4_lite = '''
package bus;

  /*=== Project imports ===*/
  import AXI4_Lite_Types::*;
  import PinTop::*;
  import pinmux::*;
  import Semi_FIFOF::*;
  /*======================*/

  interface Ifc_bus;
    interface AXI4_Lite_Slave_IFC #({0}, {1}, 0) axi_side;
    interface PeripheralSide peripheral_side;
  endinterface

  module mkbus(Ifc_bus);
    Ifc_PintTop pintop <-mkPinTop;
    AXI4_Lite_Slave_Xactor_IFC#({0}, {1}, 0) slave_xactor <-
                                                    mkAXI4_Lite_Slave_Xactor();
    rule read_transaction;
      let req<-pop_o(slave_xactor.o_rd_addr);
      let {{err,data}}=pintop.read(req.araddr);
      AXI4_Lite_Rd_Data#({0}, 0) r = AXI4_Lite_Rd_Data {{
                                  rresp: err?AXI4_LITE_SLVERR:AXI4_LITE_OKAY,
                                  rdata: zeroExtend(data) , ruser: 0}};
      slave_xactor.i_rd_data.enq(r);
    endrule

    rule write_transaction;
      let addr_req<-pop_o(slave_xactor.o_wr_addr);
      let data_req<-pop_o(slave_xactor.o_wr_data);
      let err<-pintop.write(addr_req.awaddr, data_req.wdata);
      let b = AXI4_Lite_Wr_Resp {{bresp: err?AXI4_LITE_SLVERR:AXI4_LITE_OKAY,
                                buser: ?}};
      slave_xactor.i_wr_resp.enq (b);
    endrule
    interface axi_side= slave_xactor.axi_side;
    interface peripheral_side=pintop.peripheral_side;
  endmodule
endpackage
'''
