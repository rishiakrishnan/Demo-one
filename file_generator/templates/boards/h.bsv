/* 
Copyright (c) 2019, IIT Madras All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions
  and the following disclaimer.  
* Redistributions in binary form must reproduce the above copyright notice, this list of 
  conditions and the following disclaimer in the documentation and/or other materials provided 
 with the distribution.  
* Neither the name of IIT Madras  nor the names of its contributors may be used to endorse or 
  promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------------------------------

Author: Neel Gala
Email id: neelgala@gmail.com
Details:

--------------------------------------------------------------------------------------------------
*/
package uart_cluster;
	import AXI4_Lite_Types:: *;
	import AXI4_Lite_Fabric:: *;
  import uart::*;
  import err_slave::*;
  import Connectable:: *;
  import GetPut:: *;
  
  `include "Soc.defines"

  function Bit#(TLog#(`UARTCluster_Num_Slaves)) fn_slave_map (Bit#(`paddr) addr);
    Bool slave_exist = True;
    Bit#(TLog#(`UARTCluster_Num_Slaves)) slave_num = 0;
    {% for i in range(uart) %}
    {% if i == 0 %}
        if(     addr>= `UART{{i}}Base && addr<= `UART{{i}}End )
      slave_num =  `UART{{i}}_slave_num;
    {% else %}
        else if(addr>= `UART{{i}}Base && addr<= `UART{{i}}End )
      slave_num =  `UART1_slave_num;
    {% endif %}
{% endfor %}
    else
      slave_num = `UARTCluster_err_slave_num;
      
    return slave_num;
  endfunction:fn_slave_map

  interface Ifc_uart_cluster;
  {% for i in range(uart) %}

  interface RS232 uart{{uart}}_io;
  
  {% endfor %}
//  interface RS232 uart2_io;
interface AXI4_Lite_Slave_IFC#({{paddr}}, {{daddr}}, {{config}}) slave;
    method Bit#(3) uart_interrupts;
  endinterface

  (*synthesize*)
  module mkuart(Ifc_uart_axi4lite#(32, 32, 0, 16));
	  let core_clock<-exposeCurrentClock;
  	let core_reset<-exposeCurrentReset;
    let ifc();
    `ifdef simulate
      mkuart_axi4lite#(core_clock, core_reset, 5, 0, 0) _temp(ifc);
    `else
        mkuart_axi4lite#(core_clock, core_reset, 163, 0, 0) _temp(ifc);
    `endif
    return ifc;
  endmodule

  (*synthesize*)
  module mkuart_cluster(Ifc_uart_cluster);
    let curr_clk<- exposeCurrentClock;
    let curr_reset <- exposeCurrentReset;
	AXI4_Lite_Master_Xactor_IFC #({{paddr}}, {{daddr}}, {{config}}) c2m_xactor <- mkAXI4_Lite_Master_Xactor;
	AXI4_Lite_Slave_Xactor_IFC #({{paddr}}, {{daddr}}, {{config}}) c2s_xactor <- mkAXI4_Lite_Slave_Xactor;
    AXI4_Lite_Fabric_IFC #(`UARTCluster_Num_Masters, `UARTCluster_Num_Slaves, {{paddr}}, 32,0) 
                                                    fabric <- mkAXI4_Lite_Fabric(fn_slave_map);
{% for i in range(uart) %}
let uart{{uart}} <- mkuart();																									
{% endfor %}
//  let uart2 <- mkuart();
Ifc_err_slave_axi4lite#({{paddr}}, {{daddr}}, {{config}} ) err_slave <- mkerr_slave_axi4lite;
   	
   	mkConnection(c2m_xactor.axi_side, fabric.v_from_masters[0]);

    mkConnection(c2s_xactor.o_wr_addr,c2m_xactor.i_wr_addr);
    mkConnection(c2s_xactor.o_wr_data,c2m_xactor.i_wr_data);
    mkConnection(c2m_xactor.o_wr_resp,c2s_xactor.i_wr_resp);
    mkConnection(c2s_xactor.o_rd_addr,c2m_xactor.i_rd_addr);
    mkConnection(c2m_xactor.o_rd_data,c2s_xactor.i_rd_data);
		
    {% for i in range(uart) %}

    mkConnection (fabric.v_to_slaves [`UART{{i}}_slave_num ],uart{{i}}.slave);
    
    {% endfor %}
//  mkConnection (fabric.v_to_slaves [`UART2_slave_num ],uart2.slave);
    mkConnection (fabric.v_to_slaves [`UARTCluster_err_slave_num ] , err_slave.slave);

    {% for i in range(uart) %}

interface uart{{i}}_io=uart{{i}}.io;

{% endfor %}
//    interface uart2_io=uart2.io;
    interface slave= c2s_xactor.axi_side;
		method Bit#(3) uart_interrupts;
			return {1'b0, 
			{% set sorted_uart = UART_uart|sort(reverse=true) %}

			{% for i in range(uart)%}
				uart{{i}}.interrupt{% if not loop.last %}, {% endif %}
			{% endfor %}
			
			};
			//return {uart2.interrupt, uart1.interrupt, uart0.interrupt};
		endmethod
  endmodule
endpackage

