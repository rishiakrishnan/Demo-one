/*
Copyright (c) 2013, IIT Madras
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

*  Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
*  Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
*  Neither the name of IIT Madras  nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

------------------------------------------------------------------------

*/
// Copyright (c) 2017 Bluespec, Inc.  All Rights Reserved

package AXI4_Lite_Types;

// ================================================================
// BSV library imports

import FIFOF       :: *;
import Connectable :: *;

// ----------------
// BSV additional libs

import Semi_FIFOF :: *;

// ****************************************************************
// ****************************************************************
// Section: RTL-level interfaces
// ****************************************************************
// ****************************************************************

// ================================================================
// These are the signal-level interfaces for an AXI4-Lite master.
// The (*..*) attributes ensure that when bsc compiles this to Verilog,
// we get exactly the signals specified in the ARM spec.

interface AXI4_Lite_Slave_IFC #(numeric type wd_addr,
				numeric type wd_data,
				numeric type wd_user);
   // Wr Addr channel
   (* always_ready, always_enabled *)
   method Action m_awvalid ((* port="awvalid" *) Bool           awvalid,    // in
			    (* port="awaddr" *)  Bit #(wd_addr) awaddr,     // in
			    (* port="awsize" *)   Bit #(3) awsize,						// in
			    (* port="awuser" *)  Bit #(wd_user) awuser);    // in
   (* always_ready, result="awready" *)
   method Bool m_awready;                                                   // out

   // Wr Data channel
   (* always_ready, always_enabled *)
   method Action m_wvalid ((* port="wvalid" *) Bool                     wvalid,    // in
			   (* port="wdata" *)  Bit #(wd_data)           wdata,     // in
			   (* port="wstrb" *)  Bit #(TDiv #(wd_data,8)) wstrb);    // in
   (* always_ready, result="wready" *)
   method Bool m_wready;                                                           // out

   // Wr Response channel
   (* always_ready, result="bvalid" *)  method Bool           m_bvalid;                                 // out
   (* always_ready, result="bresp" *)   method Bit #(2)       m_bresp;                                  // out
   (* always_ready, result="buser" *)   method Bit #(wd_user) m_buser;                                  // out
   (* always_ready, always_enabled *)   method Action m_bready  ((* port="bready" *)   Bool bready);    // in

   // Rd Addr channel
   (* always_ready, always_enabled *)
   method Action m_arvalid ((* port="arvalid" *) Bool           arvalid,    // in
			    (* port="araddr" *)  Bit #(wd_addr) araddr,     // in
				 (* port="arsize" *)	 Bit #(3)  arsize,        // in
			    (* port="aruser" *)  Bit #(wd_user) aruser);    // in
   (* always_ready, result="arready" *)
   method Bool m_arready;                                                   // out

   // Rd Data channel
   (* always_ready, result="rvalid" *)  method Bool           m_rvalid;                                 // out
   (* always_ready, result="rresp" *)   method Bit #(2)       m_rresp;                                  // out
   (* always_ready, result="rdata" *)   method Bit #(wd_data) m_rdata;                                  // out
   (* always_ready, result="ruser" *)   method Bit #(wd_user) m_ruser;                                  // out
   (* always_ready, always_enabled *)   method Action m_rready  ((* port="rready" *)   Bool rready);    // in
endinterface: AXI4_Lite_Slave_IFC
// ================================================================
// Higher-level types for payloads (rather than just bits)

typedef enum { AXI4_LITE_OKAY, AXI4_LITE_EXOKAY, AXI4_LITE_SLVERR, AXI4_LITE_DECERR } AXI4_Lite_Resp
deriving (Bits, Eq, FShow);

// Write Address channel

typedef struct {
   Bit #(wd_addr)  awaddr;
   Bit #(wd_user)  awuser;
	Bit#(3) 				awsize;
   } AXI4_Lite_Wr_Addr #(numeric type wd_addr, numeric type wd_user)
deriving (Bits, FShow);

// Write Data channel

typedef struct {
   Bit #(wd_data)             wdata;
   Bit #(TDiv #(wd_data, 8))  wstrb;
   } AXI4_Lite_Wr_Data #(numeric type wd_data)
deriving (Bits, FShow);

// Write Response channel

typedef struct {
   AXI4_Lite_Resp  bresp;
   Bit #(wd_user)  buser;
   } AXI4_Lite_Wr_Resp #(numeric type wd_user)
deriving (Bits, FShow);

// Read Address channel

typedef struct {
   Bit #(wd_addr)  araddr;
   Bit #(wd_user)  aruser;
	Bit#(3)			 arsize;
   } AXI4_Lite_Rd_Addr #(numeric type wd_addr, numeric type wd_user)
deriving (Bits, FShow);

// Read Data channel

typedef struct {
   AXI4_Lite_Resp  rresp;
   Bit #(wd_data)  rdata;
   Bit #(wd_user)  ruser;
   } AXI4_Lite_Rd_Data #(numeric type wd_data, numeric type wd_user)
deriving (Bits, FShow);

// ================================================================
// Slave transactor interface

interface AXI4_Lite_Slave_Xactor_IFC #(numeric type wd_addr,
				       numeric type wd_data,
				       numeric type wd_user);
   method Action reset;

   // AXI side
   interface AXI4_Lite_Slave_IFC #(wd_addr, wd_data, wd_user) axi_side;

   // FIFOF side
   interface FIFOF_O #(AXI4_Lite_Wr_Addr #(wd_addr, wd_user)) o_wr_addr;
   interface FIFOF_O #(AXI4_Lite_Wr_Data #(wd_data))          o_wr_data;
   interface FIFOF_I #(AXI4_Lite_Wr_Resp #(wd_user))          i_wr_resp;

   interface FIFOF_O #(AXI4_Lite_Rd_Addr #(wd_addr, wd_user)) o_rd_addr;
   interface FIFOF_I #(AXI4_Lite_Rd_Data #(wd_data, wd_user)) i_rd_data;
endinterface: AXI4_Lite_Slave_Xactor_IFC

// ----------------------------------------------------------------
// Slave transactor

module mkAXI4_Lite_Slave_Xactor (AXI4_Lite_Slave_Xactor_IFC #(wd_addr, wd_data, wd_user));

   Bool unguarded = True;
   Bool guarded   = False;

   // These FIFOs are guarded on BSV side, unguarded on AXI side
   FIFOF #(AXI4_Lite_Wr_Addr #(wd_addr, wd_user)) f_wr_addr <- mkGFIFOF (unguarded, guarded);
   FIFOF #(AXI4_Lite_Wr_Data #(wd_data))          f_wr_data <- mkGFIFOF (unguarded, guarded);
   FIFOF #(AXI4_Lite_Wr_Resp #(wd_user))          f_wr_resp <- mkGFIFOF (guarded, unguarded);

   FIFOF #(AXI4_Lite_Rd_Addr #(wd_addr, wd_user)) f_rd_addr <- mkGFIFOF (unguarded, guarded);
   FIFOF #(AXI4_Lite_Rd_Data #(wd_data, wd_user)) f_rd_data <- mkGFIFOF (guarded, unguarded);

   // ----------------------------------------------------------------
   // INTERFACE

   method Action reset;
      f_wr_addr.clear;
      f_wr_data.clear;
      f_wr_resp.clear;
      f_rd_addr.clear;
      f_rd_data.clear;
   endmethod

   // AXI side
   interface axi_side = interface AXI4_Lite_Slave_IFC;
			   // Wr Addr channel
			   method Action m_awvalid (Bool           awvalid,
						    Bit #(wd_addr) awaddr,
							 Bit#(3) awsize,
						    Bit #(wd_user) awuser);
			      if (awvalid && f_wr_addr.notFull)
				 f_wr_addr.enq (AXI4_Lite_Wr_Addr {awaddr: awaddr,
									awsize:awsize,
								   awuser: awuser});
			   endmethod

			   method Bool m_awready;
			      return f_wr_addr.notFull;
			   endmethod

			   // Wr Data channel
			   method Action m_wvalid (Bool                      wvalid,
						   Bit #(wd_data)            wdata,
						   Bit #(TDiv #(wd_data, 8)) wstrb);
			      if (wvalid && f_wr_data.notFull)
				 f_wr_data.enq (AXI4_Lite_Wr_Data {wdata: wdata, wstrb: wstrb});
			   endmethod

			   method Bool m_wready;
			      return f_wr_data.notFull;
			   endmethod

			   // Wr Response channel
			   method Bool           m_bvalid = f_wr_resp.notEmpty;
			   method Bit #(2)       m_bresp  = pack (f_wr_resp.first.bresp);
			   method Bit #(wd_user) m_buser  = f_wr_resp.first.buser;
			   method Action m_bready (Bool bready);
			      if (bready && f_wr_resp.notEmpty)
				 f_wr_resp.deq;
			   endmethod

			   // Rd Addr channel
			   method Action m_arvalid (Bool           arvalid,
						    Bit #(wd_addr) araddr,
							 Bit#(3)				 arsize,
						    Bit #(wd_user) aruser);
			      if (arvalid && f_rd_addr.notFull)
				 f_rd_addr.enq (AXI4_Lite_Rd_Addr {araddr: araddr,
									arsize: arsize,
								   aruser: aruser});
			   endmethod

			   method Bool m_arready;
			      return f_rd_addr.notFull;
			   endmethod

			   // Rd Data channel
			   method Bool           m_rvalid = f_rd_data.notEmpty;
			   method Bit #(2)       m_rresp  = pack (f_rd_data.first.rresp);
			   method Bit #(wd_data) m_rdata  = f_rd_data.first.rdata;
			   method Bit #(wd_user) m_ruser  = f_rd_data.first.ruser;
			   method Action m_rready (Bool rready);
			      if (rready && f_rd_data.notEmpty)
				 f_rd_data.deq;
			   endmethod
			endinterface;

   // FIFOF side
   interface o_wr_addr = to_FIFOF_O (f_wr_addr);
   interface o_wr_data = to_FIFOF_O (f_wr_data);
   interface i_wr_resp = to_FIFOF_I (f_wr_resp);

   interface o_rd_addr = to_FIFOF_O (f_rd_addr);
   interface i_rd_data = to_FIFOF_I (f_rd_data);
endmodule: mkAXI4_Lite_Slave_Xactor

// ================================================================

endpackage
