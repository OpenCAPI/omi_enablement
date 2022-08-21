if { $argc != 4 } {
        puts "The script requires four arguments to be input. First is project name and second is project path."
    } else {
        set project_name [lindex $argv 0]
        set project_path [lindex $argv 1]
        set fire_path [lindex $argv 2]
        set xdc_path [lindex $argv 3]
        }

puts "Project name: $project_name"
puts "Project path: $project_path"
puts "Fire path: $fire_path"
puts "XDC file path: $xdc_path"

# creating new project, change path accordingly
create_project ${project_name} ${project_path}${project_name} -part xcvu37p-fsvh2892-2L-e
set_property board_part xilinx.com:vcu128:part0:1.0 [current_project]
set_property target_language VHDL [current_project]

# adding constraints file
add_files -fileset constrs_1 -norecurse $xdc_path

# adding fire IP repo
set_property  ip_repo_paths $fire_path [current_project]
update_ip_catalog

# create board design named "design 1"
create_bd_design "design_1"
update_compile_order -fileset sources_1

# adding DDR4
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:ddr4:2.2 ddr4_0
apply_board_connection -board_interface "ddr4_sdram" -ip_intf "ddr4_0/C0_DDR4" -diagram "design_1"
endgroup

    # connecting only the CLK
apply_bd_automation -rule xilinx.com:bd_rule:board -config { Board_Interface {default_100mhz_clk ( 100 MHz System differential clock ) } Manual_Source {Auto}}  [get_bd_intf_pins ddr4_0/C0_SYS_CLK]
    # connecting reset to 0

# adding the microblaze
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:microblaze:11.0 microblaze_0
endgroup

    # block automation, 32KB cache with interreupt controller
apply_bd_automation -rule xilinx.com:bd_rule:microblaze -config { axi_intc {1} axi_periph {Enabled} cache {8KB} clk {/ddr4_0/addn_ui_clkout1 (100 MHz)} cores {1} debug_module {Debug Only} ecc {None} local_mem {32KB} preset {None}}  [get_bd_cells microblaze_0]
startgroup
set_property -dict [list CONFIG.C_DATA_SIZE {32}] [get_bd_cells microblaze_0]
endgroup
    # connection automation
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Clk_xbar {Auto} Master {/microblaze_0 (Cached)} Slave {/ddr4_0/C0_DDR4_S_AXI} ddr_seg {Auto} intc_ip {New AXI SmartConnect} master_apm {0}}  [get_bd_intf_pins ddr4_0/C0_DDR4_S_AXI]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Clk_xbar {/ddr4_0/addn_ui_clkout1 (100 MHz)} Master {/microblaze_0 (Periph)} Slave {/ddr4_0/C0_DDR4_S_AXI_CTRL} ddr_seg {Auto} intc_ip {/microblaze_0_axi_periph} master_apm {0}}  [get_bd_intf_pins ddr4_0/C0_DDR4_S_AXI_CTRL]
apply_bd_automation -rule xilinx.com:bd_rule:board -config { Board_Interface {Custom} Manual_Source {Auto}}  [get_bd_pins rst_ddr4_0_100M/ext_reset_in]
endgroup

    # customize it to Linux
startgroup
set_property -dict [list CONFIG.G_TEMPLATE_LIST {4} CONFIG.G_USE_EXCEPTIONS {1} CONFIG.C_USE_MSR_INSTR {1} CONFIG.C_USE_PCMP_INSTR {1} CONFIG.C_USE_BARREL {1} CONFIG.C_USE_DIV {1} CONFIG.C_USE_HW_MUL {2} CONFIG.C_UNALIGNED_EXCEPTIONS {1} CONFIG.C_ILL_OPCODE_EXCEPTION {1} CONFIG.C_M_AXI_I_BUS_EXCEPTION {1} CONFIG.C_M_AXI_D_BUS_EXCEPTION {1} CONFIG.C_DIV_ZERO_EXCEPTION {1} CONFIG.C_PVR {2} CONFIG.C_OPCODE_0x0_ILLEGAL {1} CONFIG.C_ADDR_TAG_BITS {16} CONFIG.C_CACHE_BYTE_SIZE {16384} CONFIG.C_ICACHE_LINE_LEN {8} CONFIG.C_ICACHE_VICTIMS {8} CONFIG.C_ICACHE_STREAMS {1} CONFIG.C_DCACHE_ADDR_TAG {16} CONFIG.C_DCACHE_BYTE_SIZE {16384} CONFIG.C_DCACHE_VICTIMS {8} CONFIG.C_USE_MMU {3} CONFIG.C_MMU_ZONES {2}] [get_bd_cells microblaze_0]
endgroup

# adding timer
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_timer:2.0 axi_timer_0
endgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {Auto} Clk_xbar {/ddr4_0/addn_ui_clkout1 (100 MHz)} Master {/microblaze_0 (Periph)} Slave {/axi_timer_0/S_AXI} ddr_seg {Auto} intc_ip {/microblaze_0_axi_periph} master_apm {0}}  [get_bd_intf_pins axi_timer_0/S_AXI]

# adding uart
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_uart16550:2.0 axi_uart16550_0
apply_board_connection -board_interface "rs232_uart_0" -ip_intf "axi_uart16550_0/UART" -diagram "design_1" 
endgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {Auto} Clk_xbar {/ddr4_0/addn_ui_clkout1 (100 MHz)} Master {/microblaze_0 (Periph)} Slave {/axi_uart16550_0/S_AXI} ddr_seg {Auto} intc_ip {/microblaze_0_axi_periph} master_apm {0}}  [get_bd_intf_pins axi_uart16550_0/S_AXI]

# adding i2c
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_iic:2.0 axi_iic_0
endgroup
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:board -config { Board_Interface {Custom} Manual_Source {Auto}}  [get_bd_intf_pins axi_iic_0/IIC]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {Auto} Clk_xbar {/ddr4_0/addn_ui_clkout1 (100 MHz)} Master {/microblaze_0 (Periph)} Slave {/axi_iic_0/S_AXI} ddr_seg {Auto} intc_ip {/microblaze_0_axi_periph} master_apm {0}}  [get_bd_intf_pins axi_iic_0/S_AXI]
endgroup

# adding ethernet
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_ethernet:7.2 axi_ethernet_0
apply_board_connection -board_interface "sgmii_lvds" -ip_intf "axi_ethernet_0/sgmii" -diagram "design_1" 
apply_board_connection -board_interface "mdio_mdc" -ip_intf "axi_ethernet_0/mdio" -diagram "design_1" 
apply_board_connection -board_interface "sgmii_phyclk" -ip_intf "axi_ethernet_0/lvds_clk" -diagram "design_1" 
apply_board_connection -board_interface "dummy_port_in" -ip_intf "axi_ethernet_0/dummy_port_in" -diagram "design_1" 
endgroup

    # block automation
apply_bd_automation -rule xilinx.com:bd_rule:axi_ethernet -config { FIFO_DMA {DMA} PHY_TYPE {SGMII}}  [get_bd_cells axi_ethernet_0]
    # connection automation
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config { Clk {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Freq {100} Ref_Clk0 {} Ref_Clk1 {} Ref_Clk2 {}}  [get_bd_pins axi_ethernet_0/axis_clk]
apply_bd_automation -rule xilinx.com:bd_rule:board -config { Board_Interface {Custom} Manual_Source {Auto}}  [get_bd_pins axi_ethernet_0/phy_rst_n]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {Auto} Clk_xbar {/ddr4_0/addn_ui_clkout1 (100 MHz)} Master {/microblaze_0 (Periph)} Slave {/axi_ethernet_0/s_axi} ddr_seg {Auto} intc_ip {/microblaze_0_axi_periph} master_apm {0}}  [get_bd_intf_pins axi_ethernet_0/s_axi]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Clk_xbar {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Master {/axi_ethernet_0_dma/M_AXI_MM2S} Slave {/ddr4_0/C0_DDR4_S_AXI} ddr_seg {Auto} intc_ip {/axi_smc} master_apm {0}}  [get_bd_intf_pins axi_ethernet_0_dma/M_AXI_MM2S]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Clk_xbar {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Master {/axi_ethernet_0_dma/M_AXI_S2MM} Slave {/ddr4_0/C0_DDR4_S_AXI} ddr_seg {Auto} intc_ip {/axi_smc} master_apm {0}}  [get_bd_intf_pins axi_ethernet_0_dma/M_AXI_S2MM]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Clk_xbar {/ddr4_0/c0_ddr4_ui_clk (333 MHz)} Master {/axi_ethernet_0_dma/M_AXI_SG} Slave {/ddr4_0/C0_DDR4_S_AXI} ddr_seg {Auto} intc_ip {/axi_smc} master_apm {0}}  [get_bd_intf_pins axi_ethernet_0_dma/M_AXI_SG]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/ddr4_0/addn_ui_clkout1 (100 MHz)} Clk_slave {Auto} Clk_xbar {/ddr4_0/addn_ui_clkout1 (100 MHz)} Master {/microblaze_0 (Periph)} Slave {/axi_ethernet_0_dma/S_AXI_LITE} ddr_seg {Auto} intc_ip {/microblaze_0_axi_periph} master_apm {0}}  [get_bd_intf_pins axi_ethernet_0_dma/S_AXI_LITE]
endgroup

# xlconcat setup
startgroup
set_property -dict [list CONFIG.NUM_PORTS {7}] [get_bd_cells microblaze_0_xlconcat]
endgroup
connect_bd_net [get_bd_pins axi_timer_0/interrupt] [get_bd_pins microblaze_0_xlconcat/In0]
connect_bd_net [get_bd_pins axi_uart16550_0/ip2intc_irpt] [get_bd_pins microblaze_0_xlconcat/In1]
connect_bd_net [get_bd_pins axi_iic_0/iic2intc_irpt] [get_bd_pins microblaze_0_xlconcat/In2]
connect_bd_net [get_bd_pins axi_ethernet_0/interrupt] [get_bd_pins microblaze_0_xlconcat/In3]
connect_bd_net [get_bd_pins axi_ethernet_0/mac_irq] [get_bd_pins microblaze_0_xlconcat/In4]
connect_bd_net [get_bd_pins axi_ethernet_0_dma/mm2s_introut] [get_bd_pins microblaze_0_xlconcat/In5]
connect_bd_net [get_bd_pins axi_ethernet_0_dma/s2mm_introut] [get_bd_pins microblaze_0_xlconcat/In6]

# adding fire IP
startgroup
create_bd_cell -type ip -vlnv user.org:user:fire_top:1.1 fire_top_0
endgroup

# making its pins external
startgroup
make_bd_pins_external  [get_bd_cells fire_top_0]
make_bd_intf_pins_external  [get_bd_cells fire_top_0]
endgroup
delete_bd_objs [get_bd_nets RAW_SYSCLK_0_1] [get_bd_ports RAW_SYSCLK_0]
delete_bd_objs [get_bd_nets OCDE_0_1] [get_bd_ports OCDE_0]

set_property name DDIMMA_FPGA_LANE_N [get_bd_ports DDIMMA_FPGA_LANE_N_0]
set_property name DDIMMA_FPGA_LANE_P [get_bd_ports DDIMMA_FPGA_LANE_P_0]
set_property name DDIMMA_FPGA_REFCLK_N [get_bd_ports DDIMMA_FPGA_REFCLK_N_0]
set_property name DDIMMA_FPGA_REFCLK_P [get_bd_ports DDIMMA_FPGA_REFCLK_P_0]
set_property name DDIMMB_FPGA_LANE_N [get_bd_ports DDIMMB_FPGA_LANE_N_0]
set_property name DDIMMB_FPGA_LANE_P [get_bd_ports DDIMMB_FPGA_LANE_P_0]
set_property name DDIMMB_FPGA_REFCLK_N [get_bd_ports DDIMMB_FPGA_REFCLK_N_0]
set_property name DDIMMB_FPGA_REFCLK_P [get_bd_ports DDIMMB_FPGA_REFCLK_P_0]
set_property name fpga_ddimma_mfg_tapsel_i [get_bd_ports fpga_ddimma_mfg_tapsel_i_0]
set_property name fpga_ddimmb_mfg_tapsel_i [get_bd_ports fpga_ddimmb_mfg_tapsel_i_0]
set_property name DDIMMA_RESETN [get_bd_ports DDIMMA_RESETN_0]
set_property name DDIMMB_RESETN [get_bd_ports DDIMMB_RESETN_0]
set_property name SCL_IO [get_bd_ports SCL_IO_0]
set_property name SDA_IO [get_bd_ports SDA_IO_0]
set_property name GPIO_LED_0 [get_bd_ports GPIO_LED_0_0]
set_property name GPIO_LED_1 [get_bd_ports GPIO_LED_1_0]
set_property name GPIO_LED_2 [get_bd_ports GPIO_LED_2_0]
set_property name GPIO_LED_3 [get_bd_ports GPIO_LED_3_0]
set_property name GPIO_LED_4 [get_bd_ports GPIO_LED_4_0]
set_property name GPIO_LED_5 [get_bd_ports GPIO_LED_5_0]
set_property name GPIO_LED_6 [get_bd_ports GPIO_LED_6_0]
set_property name GPIO_LED_7 [get_bd_ports GPIO_LED_7_0]
set_property name FPGA_DDIMMA_LANE_N [get_bd_ports FPGA_DDIMMA_LANE_N_0]
set_property name FPGA_DDIMMA_LANE_P [get_bd_ports FPGA_DDIMMA_LANE_P_0]
set_property name FPGA_DDIMMB_LANE_N [get_bd_ports FPGA_DDIMMB_LANE_N_0]
set_property name FPGA_DDIMMB_LANE_P [get_bd_ports FPGA_DDIMMB_LANE_P_0]

# adding clock wizard and connecting fire clk and reset
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0
endgroup
set_property -dict [list CONFIG.PRIM_SOURCE {Differential_clock_capable_pin}] [get_bd_cells clk_wiz_0]
connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins fire_top_0/RAW_SYSCLK]
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:board -config { Board_Interface {Custom} Manual_Source {Auto}}  [get_bd_intf_pins clk_wiz_0/CLK_IN1_D]
apply_bd_automation -rule xilinx.com:bd_rule:board -config { Board_Interface {reset ( FPGA Reset ) } Manual_Source {Auto}}  [get_bd_pins clk_wiz_0/reset]
connect_bd_net [get_bd_ports reset] [get_bd_pins fire_top_0/OCDE]


regenerate_bd_layout
save_bd_design

# generating wrapper
make_wrapper -files [get_files ${project_path}${project_name}/${project_name}.srcs/sources_1/bd/design_1/design_1.bd] -top

# Launch bitstream
add_files -norecurse ${project_path}${project_name}/${project_name}.gen/sources_1/bd/design_1/hdl/design_1_wrapper.vhd
launch_runs impl_1 -to_step write_bitstream -jobs 56
wait_on_run impl_1
update_compile_order -fileset sources_1

# Export hardware
write_hw_platform -fixed -include_bit -force -file ${project_path}${project_name}/design_1_wrapper.xsa