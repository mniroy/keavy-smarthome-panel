#!/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
"""
KEAVY-BRAIN REV 2.0 (120.0 x 72.0 mm — fits SZOMK AK-P-08 145x90x40 PLC Box & UM72 DIN-Rail)
Industrial Modular Brain & Wired LAN Controller:
- ESP32 DevKit V1 30-Pin USB-C + WIZnet W5500 + HanRun HR911105A RJ45
- 24V DC Input + Reverse Polarity Protection + 3A Fuse + SMBJ28A TVS + XL1509-5.0 Buck + AMS1117-3.3 (ETH)
- REV 2.0 Hot-Swap & EMI Hardened KEAVY-BUS Master:
  * Dedicated AMS1117-3.3 (U5_BUS) for +3V3_BUS (isolated from ESP32's 3.3V regulator!)
  * Dual 500mA SMD PTC Polyfuses (F_5V, F_3V3) for short-circuit & hot-plug protection
  * 2.2k EMI-hardened I2C pull-ups + 47R series damping resistors + USBLC6-2SC6 ESD TVS
  * Shrouded Keyed IDC Box Header DC3-10P with GND shield between SDA & SCL
"""

import os
import sys
import pcbnew

PRJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PRJ_DIR))
from keavy_common import *

LOCAL_FP_DIR = os.path.join(PRJ_DIR, "libs", "ESP32.pretty")
X_SHIFT = 26.0
BOARD_W = 120.0


def build_board():
    board = pcbnew.BOARD()
    add_board_outline(board, BOARD_W)
    S = X_SHIFT

    # 1. Nets
    net_gnd = add_net(board, "GND")
    net_24v_in = add_net(board, "+24V_IN")
    net_24v_fused = add_net(board, "+24V_FUSED")
    net_24v_bus = add_net(board, "+24V_BUS")
    net_rev_gate = add_net(board, "REV_GATE")
    net_5v = add_net(board, "+5V")
    net_5v_bus = add_net(board, "+5V_BUS")
    net_3v3_eth = add_net(board, "+3V3_ETH")
    net_3v3_b_raw = add_net(board, "+3V3_B_RAW")
    net_3v3_bus = add_net(board, "+3V3_BUS")
    net_sw = add_net(board, "BUCK_SW")
    net_pwr_led = add_net(board, "PWR_LED_A")

    net_eth_clk = add_net(board, "ETH_CLK")
    net_eth_cs = add_net(board, "ETH_CS")
    net_eth_mosi = add_net(board, "ETH_MOSI")
    net_eth_miso = add_net(board, "ETH_MISO")
    net_eth_int = add_net(board, "ETH_INT")
    net_eth_rst = add_net(board, "ETH_RST")
    net_txp = add_net(board, "ETH_TXP")
    net_txn = add_net(board, "ETH_TXN")
    net_rxp = add_net(board, "ETH_RXP")
    net_rxn = add_net(board, "ETH_RXN")
    net_xi = add_net(board, "ETH_XI")
    net_xo = add_net(board, "ETH_XO")
    net_exres = add_net(board, "ETH_EXRES")
    net_1v2o = add_net(board, "ETH_1V2O")
    net_link_led = add_net(board, "ETH_LINK_LED")
    net_act_led = add_net(board, "ETH_ACT_LED")

    # KEAVY-BUS I2C & INT (ESP32 side vs 47R damped Bus side — Predictable Designs Rule #7)
    net_sda_mcu = add_net(board, "MCU_SDA")
    net_scl_mcu = add_net(board, "MCU_SCL")
    net_int_mcu = add_net(board, "MCU_INT")
    net_sda_bus = add_net(board, "I2C_SDA")
    net_scl_bus = add_net(board, "I2C_SCL")
    net_bus_int = add_net(board, "BUS_INT")

    # 2. Mounting Holes (M3)
    add_mounting_holes(board, BOARD_W, net_gnd)

    # 3. Modular ESP32 DevKit USB-C (U2) at (36.0, 11.0)
    u2 = load_fp(LOCAL_FP_DIR, "ESP32-DevKit-USB-C", "U2", "ESP32-DevKit-30P", 10.0 + S, 11.0, ref_offset=(12.7, 13.0), val_offset=(12.7, 16.0))
    set_pad_net(u2, ["14", "17"], net_gnd)
    set_pad_net(u2, "15", net_5v)
    for pnum, enet in zip(["6", "7", "8", "9", "10", "11"], [net_eth_rst, net_eth_int, net_eth_miso, net_eth_mosi, net_eth_cs, net_eth_clk]):
        set_pad_net(u2, pnum, enet)
    set_pad_net(u2, "21", net_int_mcu)
    set_pad_net(u2, "26", net_sda_mcu)
    set_pad_net(u2, "29", net_scl_mcu)
    board.Add(u2)

    add_keepout_zone(board, [(8.5 + S, 0.5), (37.0 + S, 0.5), (37.0 + S, 9.3), (8.5 + S, 9.3)])
    add_silk_text(board, "5V", 6.2 + S, 46.56, size_mm=0.85, bold=True)
    add_silk_text(board, "GND", 5.8 + S, 44.02, size_mm=0.85, bold=True)
    add_silk_text(board, "USB-C", 22.7 + S, 59.0, size_mm=1.0, bold=True)
    add_silk_text(board, "ANTENNA KEEP-OUT", 22.7 + S, 2.0, size_mm=0.85)

    # 3B. LAN Subsystem (IDENTICAL)
    j_lan = load_fp(LOCAL_FP_DIR, "RJ45_Hanrun_HR911105A_Horizontal", "J_LAN", "HR911105A LAN", 22.5, 16.0, angle=180.0, ref_offset=(-4.5, 6.0), val_offset=(-4.5, 8.0))
    set_pad_net(j_lan, "1", net_txp); set_pad_net(j_lan, "2", net_txn); set_pad_net(j_lan, "3", net_rxp)
    set_pad_net(j_lan, ["4", "5", "9", "12"], net_3v3_eth); set_pad_net(j_lan, "6", net_rxn)
    set_pad_net(j_lan, ["8", "SH"], net_gnd); set_pad_net(j_lan, "10", net_link_led); set_pad_net(j_lan, "11", net_act_led)
    board.Add(j_lan)

    u3 = load_fp(f"{KICAD_FP_DIR}/Package_QFP.pretty", "LQFP-48_7x7mm_P0.5mm", "U3", "W5500", 18.0, 38.5, ref_offset=(0.0, -6.2), val_offset=(0.0, 6.2))
    set_pad_net(u3, "1", net_txn); set_pad_net(u3, "2", net_txp)
    set_pad_net(u3, ["3", "9", "14", "16", "19", "21", "23", "29", "48"], net_gnd)
    set_pad_net(u3, ["4", "8", "11", "15", "17", "28", "43", "44", "45"], net_3v3_eth)
    set_pad_net(u3, "5", net_rxn); set_pad_net(u3, "6", net_rxp); set_pad_net(u3, "10", net_exres); set_pad_net(u3, "22", net_1v2o)
    set_pad_net(u3, "25", net_link_led); set_pad_net(u3, "27", net_act_led); set_pad_net(u3, "30", net_xi); set_pad_net(u3, "31", net_xo)
    set_pad_net(u3, "32", net_eth_clk); set_pad_net(u3, "33", net_eth_cs); set_pad_net(u3, "34", net_eth_miso)
    set_pad_net(u3, "35", net_eth_mosi); set_pad_net(u3, "36", net_eth_int); set_pad_net(u3, "37", net_eth_rst)
    board.Add(u3)

    y1 = load_fp(f"{KICAD_FP_DIR}/Crystal.pretty", "Crystal_SMD_3225-4Pin_3.2x2.5mm", "Y1", "25MHz", 18.0, 50.0, ref_offset=(0.0, -2.5), val_offset=(0.0, 2.5))
    set_pad_net(y1, "1", net_xi); set_pad_net(y1, ["2", "4"], net_gnd); set_pad_net(y1, "3", net_xo); board.Add(y1)

    # Rule #10: 25MHz Crystal Load Capacitors (18pF) + W5500 Local 100nF Decoupling
    c_y1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_Y1", "18pF", 13.2, 53.1, angle=180.0, ref_offset=(-3.2, -0.5), val_offset=(-3.2, 0.8))
    set_pad_net(c_y1, "1", net_xi); set_pad_net(c_y1, "2", net_gnd); board.Add(c_y1)

    c_y2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_Y2", "18pF", 13.2, 47.0, angle=180.0, ref_offset=(-3.2, -0.5), val_offset=(-3.2, 0.8))
    set_pad_net(c_y2, "1", net_xo); set_pad_net(c_y2, "2", net_gnd); board.Add(c_y2)

    c_w55 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_W55", "100nF", 26.8, 43.8, angle=0.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(c_w55, "1", net_3v3_eth); set_pad_net(c_w55, "2", net_gnd); board.Add(c_w55)

    r_exres = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_EX", "12.4k", 7.0, 38.5, angle=180.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(r_exres, "1", net_exres); set_pad_net(r_exres, "2", net_gnd); board.Add(r_exres)

    c_1v2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_1V2", "100nF", 7.0, 44.5, angle=180.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(c_1v2, "1", net_1v2o); set_pad_net(c_1v2, "2", net_gnd); board.Add(c_1v2)

    u4 = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", "U4", "AMS1117-3.3", 18.0, 60.0, ref_offset=(0.0, -6.5), val_offset=(0.0, -5.2))
    set_pad_net(u4, "1", net_gnd); set_pad_net(u4, ["2", "4"], net_3v3_eth); set_pad_net(u4, "3", net_5v); board.Add(u4)

    c_eth_in = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_E1", "10uF", 10.5, 62.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(c_eth_in, "1", net_5v); set_pad_net(c_eth_in, "2", net_gnd); board.Add(c_eth_in)

    c_eth_out = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_E2", "10uF", 26.5, 60.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(c_eth_out, "1", net_3v3_eth); set_pad_net(c_eth_out, "2", net_gnd); board.Add(c_eth_out)

    # 4. Power Input & Protection (Rule #9: 24V Input EMI Filter Cap right at J1)
    j1 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal", "J1", "24V_IN", 73.0, 7.5, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(j1, "1", net_24v_in); set_pad_net(j1, "2", net_gnd); board.Add(j1)
    j1_p1, j1_p2 = pad_xy(j1, "1"), pad_xy(j1, "2")
    add_silk_text(board, "+24V", j1_p1[0], 15.2, size_mm=0.85, bold=True)
    add_silk_text(board, "-GND", j1_p2[0], 15.2, size_mm=0.85, bold=True)

    c_emi_in = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_EMI", "100nF 50V", 75.5, 16.8, show_val=False, ref_offset=(-3.2, 0.0))
    set_pad_net(c_emi_in, "1", net_24v_in); set_pad_net(c_emi_in, "2", net_gnd); board.Add(c_emi_in)

    f1 = load_fp(f"{KICAD_FP_DIR}/Fuse.pretty", "Fuseholder_Blade_Mini_Keystone_3568", "F1", "3A FUSE", 82.0, 6.0, ref_offset=(4.96, -3.5), val_offset=(4.96, 6.5))
    set_pad_net(f1, "1", net_24v_in); set_pad_net(f1, "2", net_24v_fused); board.Add(f1)

    q_rev = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "TO-252-3_TabPin2", "Q_REV", "AOD403", 102.0, 8.5, ref_offset=(0.0, -5.8), val_offset=(0.0, -4.6))
    set_pad_net(q_rev, "1", net_rev_gate); set_pad_net(q_rev, ["2", ""], net_24v_fused); set_pad_net(q_rev, "3", net_24v_bus); board.Add(q_rev)

    dz1 = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SOD-123", "DZ1", "BZT52C12", 97.0, 16.5, angle=180.0, ref_offset=(0.0, -2.0), val_offset=(0.0, 2.0))
    set_pad_net(dz1, "1", net_24v_bus); set_pad_net(dz1, "2", net_rev_gate); board.Add(dz1)

    r_rev = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_REV", "100k", 104.0, 16.5, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(r_rev, "1", net_rev_gate); set_pad_net(r_rev, "2", net_gnd); board.Add(r_rev)

    d_tvs = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SMB", "D_TVS", "SMBJ28A", 112.5, 19.5, ref_offset=(0.0, -3.1), val_offset=(0.0, 3.1))
    set_pad_net(d_tvs, "1", net_24v_bus); set_pad_net(d_tvs, "2", net_gnd); board.Add(d_tvs)

    # 5. Buck Converter 24V -> 5V (XL1509-5.0)
    c4 = load_fp(f"{KICAD_FP_DIR}/Capacitor_THT.pretty", "CP_Radial_D6.3mm_P2.50mm", "C4", "100uF 35V", 70.5, 23.0, angle=-90.0, ref_offset=(0.0, -4.8), val_offset=(0.0, 6.0))
    set_pad_net(c4, "1", net_24v_bus); set_pad_net(c4, "2", net_gnd); board.Add(c4)

    u1 = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-8_3.9x4.9mm_P1.27mm", "U1", "XL1509-5.0", 80.0, 23.5, ref_offset=(0.0, -3.5), val_offset=(7.0, -7.0))
    set_pad_net(u1, "1", net_24v_bus); set_pad_net(u1, "2", net_sw); set_pad_net(u1, "3", net_5v); set_pad_net(u1, ["4", "5", "6", "7", "8"], net_gnd); board.Add(u1)

    # Rule #8: Tight Switching Regulator Hot-Loop Ceramic Bypass (100nF 50V right at U1 VIN/GND, zero vias!)
    c_buck_in = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_BIN", "100nF 50V", 80.0, 17.6, show_val=False, ref_offset=(0.0, -1.8))
    set_pad_net(c_buck_in, "1", net_24v_bus); set_pad_net(c_buck_in, "2", net_gnd); board.Add(c_buck_in)

    d_buck = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SMA", "D_BUCK", "SS34", 80.0, 30.0, ref_offset=(0.0, -2.6), val_offset=(0.0, 2.6))
    set_pad_net(d_buck, "1", net_sw); set_pad_net(d_buck, "2", net_gnd); board.Add(d_buck)

    l1 = load_fp(f"{KICAD_FP_DIR}/Inductor_SMD.pretty", "L_Bourns_SRN6045TA", "L1", "33uH 3A", 90.5, 25.0, ref_offset=(0.0, -4.0), val_offset=(0.0, 4.0))
    set_pad_net(l1, "1", net_sw); set_pad_net(l1, "2", net_5v); board.Add(l1)

    c5 = load_fp(f"{KICAD_FP_DIR}/Capacitor_THT.pretty", "CP_Radial_D6.3mm_P2.50mm", "C5", "220uF 16V", 100.0, 25.0, ref_offset=(1.25, -4.5), val_offset=(1.25, 4.5))
    set_pad_net(c5, "1", net_5v); set_pad_net(c5, "2", net_gnd); board.Add(c5)

    c6 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C6", "100nF", 100.0, 32.0, ref_offset=(-3.2, -0.6), val_offset=(0.0, 2.0))
    set_pad_net(c6, "1", net_5v); set_pad_net(c6, "2", net_gnd); board.Add(c6)

    r_pwr = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_PWR", "1k", 65.5, 45.0, ref_offset=(0.0, -2.0), val_offset=(0.0, -3.2))
    set_pad_net(r_pwr, "1", net_5v); set_pad_net(r_pwr, "2", net_pwr_led); board.Add(r_pwr)

    d_pwr = load_fp(f"{KICAD_FP_DIR}/LED_SMD.pretty", "LED_0805_2012Metric", "D_PWR", "LED GRN", 65.5, 49.5, ref_offset=(0.0, 2.0), val_offset=(0.0, 3.2))
    set_pad_net(d_pwr, "2", net_pwr_led); set_pad_net(d_pwr, "1", net_gnd); board.Add(d_pwr)

    # 6. REV 2.0 Hot-Swap & EMI-Hardened KEAVY-BUS Stage
    # Dedicated AMS1117-3.3 (U5_BUS) for +3V3_BUS (ESP32 3.3V is NEVER loaded by external modules!)
    u5_bus = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", "U5_BUS", "AMS1117-3.3", 78.5, 51.0, ref_offset=(0.0, -5.5), val_offset=(0.0, 5.2))
    set_pad_net(u5_bus, "1", net_gnd); set_pad_net(u5_bus, ["2", "4"], net_3v3_b_raw); set_pad_net(u5_bus, "3", net_5v); board.Add(u5_bus)

    c_b1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_B1", "10uF", 72.0, 54.3, angle=-90.0, ref_offset=(-2.8, -0.6), val_offset=(-2.8, 0.9))
    set_pad_net(c_b1, "1", net_5v); set_pad_net(c_b1, "2", net_gnd); board.Add(c_b1)

    c_b2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_B2", "10uF", 85.2, 52.0, angle=-90.0, ref_offset=(0.0, 4.0), val_offset=(0.0, 5.3))
    set_pad_net(c_b2, "1", net_3v3_b_raw); set_pad_net(c_b2, "2", net_gnd); board.Add(c_b2)

    # Dual 500mA PTC Polyfuses (F_5V for +5V_BUS -> B0505S-1W, F_3V3 for +3V3_BUS -> ADuM1250 Side 1)
    f_5v = load_fp(f"{KICAD_FP_DIR}/Fuse.pretty", "Fuse_1206_3216Metric", "F_5V", "500mA PTC", 105.2, 31.5, angle=-90.0, show_val=False, ref_offset=(0.0, -3.2))
    set_pad_net(f_5v, "1", net_5v); set_pad_net(f_5v, "2", net_5v_bus); board.Add(f_5v)
    add_silk_text(board, "500mA", 104.2, 35.4, size_mm=0.8)

    f_3v3 = load_fp(f"{KICAD_FP_DIR}/Fuse.pretty", "Fuse_1206_3216Metric", "F_3V3", "500mA PTC", 89.2, 51.0, show_val=False, ref_offset=(0.0, -2.0))
    set_pad_net(f_3v3, "1", net_3v3_b_raw); set_pad_net(f_3v3, "2", net_3v3_bus); board.Add(f_3v3)
    add_silk_text(board, "500mA", 89.2, 53.0, size_mm=0.8)

    # 2.2k EMI-hardened pull-ups (R_SDA, R_SCL) + 10k (R_INT) + 47R series damping (R_DSDA, R_DSCL) + USBLC6-2SC6 ESD TVS
    r_sda = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_SDA", "2.2k", 92.5, 42.5, ref_offset=(0.0, -3.3), val_offset=(0.0, -2.0))
    set_pad_net(r_sda, "1", net_3v3_bus); set_pad_net(r_sda, "2", net_sda_mcu); board.Add(r_sda)

    r_scl = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_SCL", "2.2k", 92.5, 45.5, show_ref=False, val_offset=(0.0, 2.0))
    set_pad_net(r_scl, "1", net_3v3_bus); set_pad_net(r_scl, "2", net_scl_mcu); board.Add(r_scl)

    r_int = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_INT", "10k", 92.5, 56.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(r_int, "1", net_3v3_bus); set_pad_net(r_int, "2", net_int_mcu); board.Add(r_int)

    # Rule #7: 47R series edge-rate damping on BUS_INT as well as SDA/SCL
    r_dint = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_DINT", "47R", 98.5, 56.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(r_dint, "1", net_int_mcu); set_pad_net(r_dint, "2", net_bus_int); board.Add(r_dint)

    r_dsda = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_DSDA", "47R", 98.5, 42.5, ref_offset=(0.0, -3.3), val_offset=(0.0, -2.0))
    set_pad_net(r_dsda, "1", net_sda_mcu); set_pad_net(r_dsda, "2", net_sda_bus); board.Add(r_dsda)

    r_dscl = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_DSCL", "47R", 98.5, 45.5, show_ref=False, val_offset=(0.0, 2.0))
    set_pad_net(r_dscl, "1", net_scl_mcu); set_pad_net(r_dscl, "2", net_scl_bus); board.Add(r_dscl)

    d_esd = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "SOT-23-6", "D_ESD", "USBLC6-2SC6", 104.5, 44.0, ref_offset=(0.0, 3.0), val_offset=(0.0, 4.3))
    set_pad_net(d_esd, ["1", "6"], net_sda_bus)
    set_pad_net(d_esd, "2", net_gnd)
    set_pad_net(d_esd, ["3", "4"], net_scl_bus)
    set_pad_net(d_esd, "5", net_3v3_bus)
    board.Add(d_esd)

    # Shrouded Keyed IDC Box Header DC3-10P (REV 2.0 EMI-shielded pinout!)
    j_bus = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_OUT", "DC3-10P", BOARD_W - 7.5, BUS_Y, ref_offset=(1.0, -7.2), val_offset=(1.0, 17.2))
    assign_keavy_bus_nets(j_bus, net_5v_bus, net_gnd, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_bus)

    add_silk_text(board, "KEAVY-BRAIN REV 2.0", 86.0, 62.5, size_mm=0.85, bold=True)
    add_silk_text(board, "HOT-SWAP BUS | AK-P-08", 86.0, 65.0, size_mm=0.8)

    # 8. LAN -> W5500 -> ESP32 Routing (IDENTICAL)
    add_gnd_via_near(board, pad_xy(j_lan, "8")[0], pad_xy(j_lan, "8")[1], 0.0, 2.0, net_gnd)
    jp1, up2 = pad_xy(j_lan, "1"), pad_xy(u3, "2")
    add_route(board, [jp1, (jp1[0], 29.5), (11.4, 29.5), (11.4, up2[1]), up2], 0.22, pcbnew.F_Cu, net_txp)
    jp2, up1 = pad_xy(j_lan, "2"), pad_xy(u3, "1")
    add_via(board, jp2[0], jp2[1] + 2.0, net_txn, dia_mm=0.65, drill_mm=0.35); add_track(board, jp2[0], jp2[1], jp2[0], jp2[1] + 2.0, 0.22, pcbnew.F_Cu, net_txn)
    add_route(board, [up1, (12.2, up1[1]), (12.2, 34.5)], 0.22, pcbnew.F_Cu, net_txn); add_via(board, 12.2, 34.5, net_txn, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [(jp2[0], jp2[1] + 2.0), (jp2[0], 28.5), (12.2, 28.5), (12.2, 34.5)], 0.22, pcbnew.B_Cu, net_txn)
    jp3, up6 = pad_xy(j_lan, "3"), pad_xy(u3, "6")
    add_route(board, [jp3, (jp3[0], 27.5), (9.8, 27.5), (9.8, up6[1]), up6], 0.22, pcbnew.F_Cu, net_rxp)
    jp6, up5 = pad_xy(j_lan, "6"), pad_xy(u3, "5")
    add_via(board, jp6[0], jp6[1] + 2.0, net_rxn, dia_mm=0.65, drill_mm=0.35); add_track(board, jp6[0], jp6[1], jp6[0], jp6[1] + 2.0, 0.22, pcbnew.F_Cu, net_rxn)
    add_route(board, [up5, (10.6, up5[1]), (10.6, 36.5)], 0.22, pcbnew.F_Cu, net_rxn); add_via(board, 10.6, 36.5, net_rxn, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [(jp6[0], jp6[1] + 2.0), (jp6[0], 26.5), (10.6, 26.5), (10.6, 36.5)], 0.22, pcbnew.B_Cu, net_rxn)
    jp4, jp5, jp9, jp12 = pad_xy(j_lan, "4"), pad_xy(j_lan, "5"), pad_xy(j_lan, "9"), pad_xy(j_lan, "12")
    add_route(board, [jp12, (jp12[0], 2.2), (jp9[0], 2.2), jp9], 0.35, pcbnew.F_Cu, net_3v3_eth)
    jp10, up25 = pad_xy(j_lan, "10"), pad_xy(u3, "25")
    add_via(board, 23.4, up25[1], net_link_led, dia_mm=0.6, drill_mm=0.3); add_track(board, up25[0], up25[1], 23.4, up25[1], 0.22, pcbnew.F_Cu, net_link_led)
    add_route(board, [(23.4, up25[1]), (29.0, up25[1]), (29.0, 6.4)], 0.22, pcbnew.B_Cu, net_link_led); add_via(board, 29.0, 6.4, net_link_led, dia_mm=0.6, drill_mm=0.3)
    add_route(board, [(29.0, 6.4), (jp10[0], 6.4), jp10], 0.22, pcbnew.F_Cu, net_link_led)
    jp11, up27 = pad_xy(j_lan, "11"), pad_xy(u3, "27")
    add_via(board, 23.4, up27[1], net_act_led, dia_mm=0.6, drill_mm=0.3); add_track(board, up27[0], up27[1], 23.4, up27[1], 0.22, pcbnew.F_Cu, net_act_led)
    add_route(board, [(23.4, up27[1]), (28.2, up27[1]), (28.2, 2.5), (jp11[0], 2.5), jp11], 0.22, pcbnew.B_Cu, net_act_led)

    u3_xi, u3_xo = pad_xy(u3, "30"), pad_xy(u3, "31")
    y1_xi, y1_xo = pad_xy(y1, "1"), pad_xy(y1, "3")
    add_route(board, [u3_xi, (24.0, u3_xi[1]), (24.0, 53.1), (16.9, 53.1), y1_xi], 0.22, pcbnew.F_Cu, net_xi)
    add_route(board, [u3_xo, (24.8, u3_xo[1]), (24.8, 47.0)], 0.22, pcbnew.F_Cu, net_xo); add_via(board, 24.8, 47.0, net_xo, dia_mm=0.6, drill_mm=0.3)
    add_route(board, [(24.8, 47.0), (22.2, 47.0)], 0.22, pcbnew.B_Cu, net_xo); add_via(board, 22.2, 47.0, net_xo, dia_mm=0.6, drill_mm=0.3)
    add_route(board, [(22.2, 47.0), (19.1, 47.0), y1_xo], 0.22, pcbnew.F_Cu, net_xo)
    add_gnd_via_near(board, pad_xy(y1, "2")[0], pad_xy(y1, "2")[1], 0.0, 1.4, net_gnd)
    add_gnd_via_near(board, pad_xy(y1, "4")[0], pad_xy(y1, "4")[1], -1.5, 0.0, net_gnd)

    # Rule #10: Crystal load capacitors C_Y1 (18pF) & C_Y2 (18pF) + local W5500 decoupling C_W55 (100nF)
    cy1_p1, cy1_p2 = pad_xy(c_y1, "1"), pad_xy(c_y1, "2")
    cy2_p1, cy2_p2 = pad_xy(c_y2, "1"), pad_xy(c_y2, "2")
    add_route(board, [cy1_p1, (y1_xi[0], cy1_p1[1]), y1_xi], 0.22, pcbnew.F_Cu, net_xi)
    add_gnd_via_near(board, cy1_p2[0], cy1_p2[1], -1.4, 0.0, net_gnd)
    add_route(board, [cy2_p1, (y1_xo[0], cy2_p1[1]), y1_xo], 0.22, pcbnew.F_Cu, net_xo)
    add_gnd_via_near(board, cy2_p2[0], cy2_p2[1], -1.4, 0.0, net_gnd)

    cw55_p1, cw55_p2 = pad_xy(c_w55, "1"), pad_xy(c_w55, "2")
    add_via(board, cw55_p1[0], cw55_p1[1], net_3v3_eth, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [cw55_p1, (21.2, cw55_p1[1])], 0.35, pcbnew.B_Cu, net_3v3_eth)
    add_gnd_via_near(board, cw55_p2[0], cw55_p2[1], 1.5, 0.0, net_gnd)

    add_route(board, [pad_xy(u3, "10"), (8.0, 40.25), (8.0, 38.5), pad_xy(r_exres, "1")], 0.22, pcbnew.F_Cu, net_exres)
    add_gnd_via_near(board, pad_xy(r_exres, "2")[0], pad_xy(r_exres, "2")[1], -1.5, 0.0, net_gnd)
    add_route(board, [pad_xy(u3, "22"), (pad_xy(u3, "22")[0], 44.9), (7.95, 44.9), pad_xy(c_1v2, "1")], 0.22, pcbnew.F_Cu, net_1v2o)
    add_gnd_via_near(board, pad_xy(c_1v2, "2")[0], pad_xy(c_1v2, "2")[1], -1.5, 0.0, net_gnd)

    gnd_tl = (15.8, 36.0); add_via(board, gnd_tl[0], gnd_tl[1], net_gnd, dia_mm=0.7, drill_mm=0.35)
    for gpin, (dx, dy) in [("48", (0.0, 1.0)), ("3", (1.0, 0.0))]:
        gp = pad_xy(u3, gpin); add_route(board, [gp, (gp[0] + dx, gp[1] + dy), gnd_tl], 0.22, pcbnew.F_Cu, net_gnd)
    gnd_bot = (17.5, 41.1); add_via(board, gnd_bot[0], gnd_bot[1], net_gnd, dia_mm=0.7, drill_mm=0.35)
    for gpin, (dx, dy) in [("14", (0.0, -1.0)), ("16", (0.0, -1.0)), ("19", (0.0, -1.0)), ("21", (0.0, -1.0)), ("23", (0.0, -1.0))]:
        gp = pad_xy(u3, gpin); add_route(board, [gp, (gp[0] + dx, gp[1] + dy), gnd_bot], 0.22, pcbnew.F_Cu, net_gnd, chamfer=False)
    p9, p29 = pad_xy(u3, "9"), pad_xy(u3, "29")
    add_route(board, [p9, (12.4, p9[1]), (12.4, 39.5)], 0.22, pcbnew.F_Cu, net_gnd); add_via(board, 12.4, 39.5, net_gnd, dia_mm=0.6, drill_mm=0.3)
    add_route(board, [p29, (20.4, p29[1]), (20.4, 37.5)], 0.22, pcbnew.F_Cu, net_gnd); add_via(board, 20.4, 37.5, net_gnd, dia_mm=0.6, drill_mm=0.3)

    vdd_star = (18.2, 38.7); add_via(board, vdd_star[0], vdd_star[1], net_3v3_eth, dia_mm=0.7, drill_mm=0.35)
    for vpin, (dx, dy) in [("4", (1.0, 0.0)), ("8", (1.0, 0.0)), ("43", (0.0, 1.0)), ("44", (0.0, 1.0)), ("45", (0.0, 1.0))]:
        vp = pad_xy(u3, vpin); add_route(board, [vp, (vp[0] + dx, vp[1] + dy), vdd_star], 0.22, pcbnew.F_Cu, net_3v3_eth)
    p28 = pad_xy(u3, "28"); add_route(board, [p28, (21.0, p28[1]), (19.5, 39.75), (19.5, 38.7), vdd_star], 0.22, pcbnew.F_Cu, net_3v3_eth)
    p11 = pad_xy(u3, "11"); add_route(board, [p11, (12.4, p11[1]), (12.4, 41.5)], 0.22, pcbnew.F_Cu, net_3v3_eth); add_via(board, 12.4, 41.5, net_3v3_eth, dia_mm=0.6, drill_mm=0.3)
    vdd_out_vias = [(12.4, 41.5)]
    for vpin in ["15", "17"]:
        vp = pad_xy(u3, vpin); add_track(board, vp[0], vp[1], vp[0], 43.8, 0.22, pcbnew.F_Cu, net_3v3_eth); add_via(board, vp[0], 43.8, net_3v3_eth, dia_mm=0.6, drill_mm=0.3); vdd_out_vias.append((vp[0], 43.8))

    u4_gnd, u4_out, u4_tab, u4_in = pad_xy(u4, "1"), pad_xy(u4, "2"), pad_xy(u4, "2", "max_x"), pad_xy(u4, "3")
    add_track(board, u4_out[0], u4_out[1], u4_tab[0], u4_tab[1], 0.8, pcbnew.F_Cu, net_3v3_eth)
    add_gnd_via_near(board, u4_gnd[0], u4_gnd[1], -1.5, 0.0, net_gnd)
    ce1_p1 = pad_xy(c_eth_in, "1")
    add_route(board, [u4_in, (u4_in[0], 64.5), (ce1_p1[0], 64.5), ce1_p1], 0.6, pcbnew.F_Cu, net_5v)
    add_gnd_via_near(board, pad_xy(c_eth_in, "2")[0], pad_xy(c_eth_in, "2")[1], 1.5, 0.0, net_gnd)
    add_route(board, [u4_tab, pad_xy(c_eth_out, "1")], 0.6, pcbnew.F_Cu, net_3v3_eth)
    ce2_p1 = pad_xy(c_eth_out, "1")
    add_via(board, ce2_p1[0], ce2_p1[1] - 2.0, net_3v3_eth, dia_mm=0.8, drill_mm=0.4); add_track(board, ce2_p1[0], ce2_p1[1], ce2_p1[0], ce2_p1[1] - 2.0, 0.6, pcbnew.F_Cu, net_3v3_eth)
    add_gnd_via_near(board, pad_xy(c_eth_out, "2")[0], pad_xy(c_eth_out, "2")[1], 1.5, 0.0, net_gnd)
    add_route(board, [(ce2_p1[0], ce2_p1[1] - 2.0), (21.2, 58.0), (21.2, 43.8), vdd_out_vias[2], vdd_out_vias[1], vdd_out_vias[0]], 0.35, pcbnew.B_Cu, net_3v3_eth)
    add_route(board, [vdd_out_vias[2], (19.5, 43.8), (19.5, 38.7), vdd_star], 0.35, pcbnew.B_Cu, net_3v3_eth)
    add_route(board, [vdd_out_vias[0], (8.6, 41.5), (8.6, 15.2), (12.8, 15.2), (12.8, 13.8), (jp5[0], 13.8), jp5], 0.35, pcbnew.B_Cu, net_3v3_eth)
    add_route(board, [(jp5[0], 13.8), (jp4[0], 13.8), jp4], 0.35, pcbnew.B_Cu, net_3v3_eth)
    add_route(board, [(8.6, 15.2), (8.6, jp12[1]), jp12], 0.35, pcbnew.B_Cu, net_3v3_eth)

    u2_5v = pad_xy(u2, "15")
    add_route(board, [u2_5v, (u2_5v[0] + 5.0, u2_5v[1]), (u2_5v[0] + 5.0, 64.5), (ce1_p1[0], 64.5)], 0.6, pcbnew.B_Cu, net_5v)
    add_via(board, ce1_p1[0], 64.5, net_5v)

    for idx, (epin, wpin, snet, vx) in enumerate([("6", "37", net_eth_rst, 30.0), ("7", "36", net_eth_int, 30.85), ("9", "35", net_eth_mosi, 32.55), ("8", "34", net_eth_miso, 31.70), ("10", "33", net_eth_cs, 33.40), ("11", "32", net_eth_clk, 34.25)]):
        ep, wp = pad_xy(u2, epin), pad_xy(u3, wpin)
        vy, fx = 31.7 + idx * 0.9, 23.8 + idx * 0.45
        if wpin == "37": add_route(board, [wp, (wp[0], vy), (vx, vy)], 0.22, pcbnew.F_Cu, snet)
        else: add_route(board, [wp, (fx, wp[1]), (fx, vy), (vx, vy)], 0.22, pcbnew.F_Cu, snet)
        add_via(board, vx, vy, snet, dia_mm=0.65, drill_mm=0.35); add_route(board, [(vx, vy), (vx, ep[1]), ep], 0.22, pcbnew.B_Cu, snet)

    # Rule #4: Ground return vias adjacent to high-speed W5500 SPI layer-change vias (tied to F.Cu GND pour)
    for gx, gy in [(32.5, 29.0), (34.8, 39.2)]:
        if is_clear_for_via(board, gx, gy, min_dist_mm=1.25):
            add_via(board, gx, gy, net_gnd, dia_mm=0.70, drill_mm=0.35)

    # 9. Power Input & Buck Routing
    cemi_p1, cemi_p2 = pad_xy(c_emi_in, "1"), pad_xy(c_emi_in, "2")
    add_route(board, [j1_p1, (j1_p1[0], cemi_p1[1]), cemi_p1], 0.6, pcbnew.F_Cu, net_24v_in)
    add_gnd_via_near(board, cemi_p2[0], cemi_p2[1], 1.4, 0.0, net_gnd)
    f1_p1_top, f1_p1_bot = pad_xy(f1, "1", "min_y"), pad_xy(f1, "1", "max_y")
    f1_p2_top, f1_p2_bot = pad_xy(f1, "2", "min_y"), pad_xy(f1, "2", "max_y")
    add_track(board, f1_p1_top[0], f1_p1_top[1], f1_p1_bot[0], f1_p1_bot[1], 2.0, pcbnew.F_Cu, net_24v_in)
    add_track(board, f1_p2_top[0], f1_p2_top[1], f1_p2_bot[0], f1_p2_bot[1], 2.0, pcbnew.F_Cu, net_24v_fused)
    add_route(board, [j1_p1, (j1_p1[0], 3.0), (f1_p1_top[0], 3.0), f1_p1_top], 2.0, pcbnew.F_Cu, net_24v_in)

    qrev_tab, qrev_pin2, qrev_g, qrev_s = pad_xy(q_rev, "2", "max_x"), pad_xy(q_rev, "2", "first"), pad_xy(q_rev, "1"), pad_xy(q_rev, "3")
    add_track(board, qrev_pin2[0], qrev_pin2[1], qrev_tab[0], qrev_tab[1], 0.6, pcbnew.F_Cu, net_24v_fused)
    add_route(board, [f1_p2_top, (f1_p2_top[0], 3.0), (qrev_tab[0], 3.0), qrev_tab], 2.0, pcbnew.F_Cu, net_24v_fused)

    dz1_p1, dz1_p2 = pad_xy(dz1, "1"), pad_xy(dz1, "2")
    rrev_p1, rrev_p2 = pad_xy(r_rev, "1"), pad_xy(r_rev, "2")
    add_route(board, [qrev_g, (94.5, qrev_g[1]), (94.5, 15.0), (dz1_p2[0], 15.0), dz1_p2], 0.35, pcbnew.F_Cu, net_rev_gate)
    add_route(board, [dz1_p2, (dz1_p2[0], 18.5), (rrev_p1[0], 18.5), rrev_p1], 0.35, pcbnew.F_Cu, net_rev_gate)
    add_gnd_via_near(board, rrev_p2[0], rrev_p2[1], 1.5, 0.0, net_gnd)

    dtvs_p1, dtvs_p2 = pad_xy(d_tvs, "1"), pad_xy(d_tvs, "2")
    c4_p1 = pad_xy(c4, "1")
    add_route(board, [qrev_s, (dz1_p1[0], qrev_s[1]), dz1_p1], 0.6, pcbnew.F_Cu, net_24v_bus)
    add_route(board, [qrev_s, (qrev_s[0], 13.5), (109.0, 13.5), (109.0, 19.5), dtvs_p1], 1.5, pcbnew.F_Cu, net_24v_bus)
    add_gnd_via_near(board, dtvs_p2[0], dtvs_p2[1], 1.8, 0.0, net_gnd)
    add_route(board, [(109.0, 13.5), (109.0, 20.0), (70.5, 20.0), c4_p1], 1.2, pcbnew.F_Cu, net_24v_bus)

    u1_p1, u1_p2, u1_p3, u1_p4, u1_p5, u1_p8 = [pad_xy(u1, str(k)) for k in (1, 2, 3, 4, 5, 8)]
    add_route(board, [c4_p1, (c4_p1[0], u1_p1[1]), u1_p1], 1.0, pcbnew.F_Cu, net_24v_bus)
    # Rule #8: Connect C_BIN (100nF 50V) directly at U1 VIN & GND (shortest hot loop!)
    cbin_p1, cbin_p2 = pad_xy(c_buck_in, "1"), pad_xy(c_buck_in, "2")
    add_route(board, [cbin_p1, (cbin_p1[0], 20.0)], 0.5, pcbnew.F_Cu, net_24v_bus)
    add_gnd_via_near(board, cbin_p2[0], cbin_p2[1], 1.5, 0.0, net_gnd)
    dbuck_p1, dbuck_p2 = pad_xy(d_buck, "1"), pad_xy(d_buck, "2")
    l1_p1, l1_p2 = pad_xy(l1, "1"), pad_xy(l1, "2")
    c5_p1, c5_p2 = pad_xy(c5, "1"), pad_xy(c5, "2")
    c6_p1, c6_p2 = pad_xy(c6, "1"), pad_xy(c6, "2")

    add_route(board, [u1_p2, (74.0, u1_p2[1]), (74.0, 30.0), dbuck_p1], 1.0, pcbnew.F_Cu, net_sw)
    add_route(board, [dbuck_p1, (dbuck_p1[0], 32.5), (86.2, 32.5), (86.2, l1_p1[1]), l1_p1], 1.0, pcbnew.F_Cu, net_sw)
    add_gnd_via_near(board, dbuck_p2[0], dbuck_p2[1], 1.8, 0.0, net_gnd)
    add_track(board, u1_p4[0], u1_p4[1], u1_p5[0], u1_p5[1], 0.4, pcbnew.F_Cu, net_gnd)
    add_track(board, u1_p5[0], u1_p5[1], u1_p8[0], u1_p8[1], 0.6, pcbnew.F_Cu, net_gnd)
    add_gnd_via_near(board, u1_p8[0], u1_p8[1], 1.8, 0.0, net_gnd)

    add_route(board, [l1_p2, c5_p1], 1.2, pcbnew.F_Cu, net_5v)
    add_route(board, [c5_p1, (98.5, c5_p1[1]), (98.5, c6_p1[1]), c6_p1], 0.5, pcbnew.F_Cu, net_5v)
    add_gnd_via_near(board, c6_p2[0], c6_p2[1], 1.5, 0.0, net_gnd)

    add_route(board, [u1_p3, (75.8, u1_p3[1]), (75.8, 26.5)], 0.3, pcbnew.F_Cu, net_5v); add_via(board, 75.8, 26.5, net_5v)
    add_route(board, [(75.8, 26.5), (75.8, 27.5), (96.0, 27.5), (96.0, c5_p1[1])], 0.35, pcbnew.B_Cu, net_5v)
    add_via(board, 96.0, c5_p1[1], net_5v); add_track(board, 96.0, c5_p1[1], c5_p1[0], c5_p1[1], 0.4, pcbnew.F_Cu, net_5v)

    rpwr_p1, rpwr_p2 = pad_xy(r_pwr, "1"), pad_xy(r_pwr, "2")
    dpwr_p1, dpwr_p2 = pad_xy(d_pwr, "1"), pad_xy(d_pwr, "2")
    add_via(board, c5_p1[0], c5_p1[1] + 2.5, net_5v); add_track(board, c5_p1[0], c5_p1[1], c5_p1[0], c5_p1[1] + 2.5, 0.6, pcbnew.F_Cu, net_5v)
    add_route(board, [(c5_p1[0], c5_p1[1] + 2.5), (100.0, 27.51), (58.0, 27.51), (58.0, 45.28), (64.5, 45.28)], 0.4, pcbnew.B_Cu, net_5v)
    add_via(board, 64.5, 45.28, net_5v); add_track(board, 64.5, 45.28, rpwr_p1[0], rpwr_p1[1], 0.5, pcbnew.F_Cu, net_5v)
    add_track(board, rpwr_p2[0], rpwr_p2[1], dpwr_p2[0], dpwr_p2[1], 0.3, pcbnew.F_Cu, net_pwr_led)
    add_gnd_via_near(board, dpwr_p1[0], dpwr_p1[1], -1.5, 0.0, net_gnd)
    add_route(board, [(58.0, 27.51), (48.0, 27.51), (48.0, u2_5v[1]), u2_5v], 0.8, pcbnew.B_Cu, net_5v)

    # 10. REV 2.0 Hot-Swap KEAVY-BUS Power & Signal Routing
    jb1, jb2, jb5 = pad_xy(j_bus, "1"), pad_xy(j_bus, "2"), pad_xy(j_bus, "5")
    jb7, jb9, jb10 = pad_xy(j_bus, "7"), pad_xy(j_bus, "9"), pad_xy(j_bus, "10")

    # +5V -> F_5V -> +5V_BUS -> J_BUS_OUT (1,2)
    f5_p1, f5_p2 = pad_xy(f_5v, "1"), pad_xy(f_5v, "2")
    add_route(board, [c5_p1, (c5_p1[0], 29.0), (f5_p1[0], 29.0), f5_p1], 0.6, pcbnew.F_Cu, net_5v)
    add_route(board, [f5_p2, (108.5, f5_p2[1]), (108.5, jb1[1]), jb1, jb2], 0.6, pcbnew.F_Cu, net_5v_bus)

    # +5V -> C_B1 -> U5_BUS (AMS1117-3.3) -> C_B2 -> F_3V3 -> +3V3_BUS
    u5_gnd, u5_out, u5_tab, u5_in = pad_xy(u5_bus, "1"), pad_xy(u5_bus, "2"), pad_xy(u5_bus, "2", "max_x"), pad_xy(u5_bus, "3")
    cb1_p1, cb1_p2 = pad_xy(c_b1, "1"), pad_xy(c_b1, "2")
    cb2_p1, cb2_p2 = pad_xy(c_b2, "1"), pad_xy(c_b2, "2")
    f3_p1, f3_p2 = pad_xy(f_3v3, "1"), pad_xy(f_3v3, "2")

    add_route(board, [(64.5, 45.28), (64.5, 53.35), (70.2, 53.35)], 0.5, pcbnew.B_Cu, net_5v)
    add_via(board, 70.2, 53.35, net_5v, dia_mm=0.7, drill_mm=0.35)
    add_route(board, [(70.2, 53.35), cb1_p1, (cb1_p1[0], u5_in[1]), u5_in], 0.5, pcbnew.F_Cu, net_5v)
    add_gnd_via_near(board, cb1_p2[0], cb1_p2[1], 0.0, 1.6, net_gnd)
    add_gnd_via_near(board, u5_gnd[0], u5_gnd[1], -1.5, 0.0, net_gnd)
    add_track(board, u5_out[0], u5_out[1], u5_tab[0], u5_tab[1], 0.8, pcbnew.F_Cu, net_3v3_b_raw)
    add_route(board, [u5_tab, (cb2_p1[0], u5_tab[1]), cb2_p1, (cb2_p1[0], f3_p1[1]), f3_p1], 0.5, pcbnew.F_Cu, net_3v3_b_raw)
    add_gnd_via_near(board, cb2_p2[0], cb2_p2[1], 0.0, 1.6, net_gnd)

    # +3V3_BUS fanout: F_3V3(2) -> R_SDA(1), R_SCL(1), R_INT(1), D_ESD(5), J_BUS_OUT(5)
    rsda_p1, rsda_p2 = pad_xy(r_sda, "1"), pad_xy(r_sda, "2")
    rscl_p1, rscl_p2 = pad_xy(r_scl, "1"), pad_xy(r_scl, "2")
    rint_p1, rint_p2 = pad_xy(r_int, "1"), pad_xy(r_int, "2")
    esd_1, esd_2, esd_3, esd_4, esd_5, esd_6 = [pad_xy(d_esd, str(k)) for k in range(1, 7)]

    add_route(board, [f3_p2, (rsda_p1[0], f3_p2[1]), (rsda_p1[0], rint_p1[1]), rint_p1], 0.35, pcbnew.F_Cu, net_3v3_bus)
    add_route(board, [(rsda_p1[0], f3_p2[1]), rscl_p1, rsda_p1], 0.35, pcbnew.F_Cu, net_3v3_bus)
    add_route(board, [rsda_p1, (rsda_p1[0], 36.08), jb5], 0.35, pcbnew.F_Cu, net_3v3_bus)
    add_via(board, 107.2, 36.08, net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [(107.2, 36.08), (107.2, esd_5[1])], 0.25, pcbnew.B_Cu, net_3v3_bus)
    add_via(board, 107.2, esd_5[1], net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, 107.2, esd_5[1], esd_5[0], esd_5[1], 0.25, pcbnew.F_Cu, net_3v3_bus)

    # ESP32 -> MCU_SDA/SCL & BUS_INT -> Pull-ups -> 47R damping -> USBLC6 -> J_BUS_OUT
    rdsda_p1, rdsda_p2 = pad_xy(r_dsda, "1"), pad_xy(r_dsda, "2")
    rdscl_p1, rdscl_p2 = pad_xy(r_dscl, "1"), pad_xy(r_dscl, "2")
    add_track(board, rsda_p2[0], rsda_p2[1], rdsda_p1[0], rdsda_p1[1], 0.22, pcbnew.F_Cu, net_sda_mcu)
    add_track(board, rscl_p2[0], rscl_p2[1], rdscl_p1[0], rdscl_p1[1], 0.22, pcbnew.F_Cu, net_scl_mcu)
    add_route(board, [rdsda_p2, (rdsda_p2[0], esd_1[1]), esd_1, esd_6, (108.6, esd_6[1]), (108.6, jb7[1]), jb7], 0.22, pcbnew.F_Cu, net_sda_bus)
    add_route(board, [rdscl_p2, (rdscl_p2[0], esd_3[1]), esd_3, esd_4, (109.6, esd_4[1]), (109.6, jb9[1]), jb9], 0.22, pcbnew.F_Cu, net_scl_bus)
    add_gnd_via_near(board, esd_2[0], esd_2[1], -1.5, 0.0, net_gnd)

    # Route ESP32 Pad 29 (SCL), Pad 26 (SDA), Pad 21 (INT) cleanly on B.Cu with zero crossings
    for epin, snet, cx, by, vx_r, target in [
        ("29", net_scl_mcu, 65.5, 38.0, 95.8, rscl_p2),
        ("26", net_sda_mcu, 64.7, 38.8, 95.0, rsda_p2),
        ("21", net_int_mcu, 63.9, 39.6, 94.2, rint_p2),
    ]:
        ep = pad_xy(u2, epin)
        vx_l = 67.2 + (39.6 - by) * 1.1
        add_route(board, [ep, (cx, ep[1]), (cx, by), (vx_l, by)], 0.22, pcbnew.F_Cu, snet)
        add_via(board, vx_l, by, snet, dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(vx_l, by), (vx_r, by), (vx_r, target[1])], 0.22, pcbnew.B_Cu, snet)
        add_via(board, vx_r, target[1], snet, dia_mm=0.60, drill_mm=0.30)
        add_track(board, vx_r, target[1], target[0], target[1], 0.22, pcbnew.F_Cu, snet)

    # BUS_INT: R_INT(2) -> R_DINT (47R series damping) -> J_BUS_OUT(10) cleanly on B.Cu
    rdint_p1, rdint_p2 = pad_xy(r_dint, "1"), pad_xy(r_dint, "2")
    add_track(board, rint_p2[0], rint_p2[1], rdint_p1[0], rdint_p1[1], 0.22, pcbnew.F_Cu, net_int_mcu)
    add_via(board, rdint_p2[0] + 1.4, rdint_p2[1], net_bus_int, dia_mm=0.60, drill_mm=0.30)
    add_track(board, rdint_p2[0], rdint_p2[1], rdint_p2[0] + 1.4, rdint_p2[1], 0.22, pcbnew.F_Cu, net_bus_int)
    add_route(board, [(rdint_p2[0] + 1.4, rdint_p2[1]), (jb10[0], rdint_p2[1]), jb10], 0.22, pcbnew.B_Cu, net_bus_int)

    # Rule #4: Perimeter Ground Stitching Vias (skipping ESP32 antenna keepout)
    add_perimeter_gnd_stitching(board, BOARD_W, net_gnd, skip_boxes=[(8.0 + S, 0.0, 38.0 + S, 10.5)])

    # 11. Copper Pours
    add_zone(board, net_gnd, pcbnew.B_Cu, [(1.0, 1.0), (BOARD_W - 1.0, 1.0), (BOARD_W - 1.0, BOARD_H - 1.0), (1.0, BOARD_H - 1.0)], priority=0, clearance_mm=0.35)
    add_zone(board, net_gnd, pcbnew.F_Cu, [(32.0, 12.0), (40.5 + S, 12.0), (40.5 + S, 70.0), (32.0, 70.0)], priority=0, clearance_mm=0.45)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_path = os.path.join(PRJ_DIR, "keavy_brain.kicad_pcb")
    board.Save(out_path)
    print(f"Successfully generated: {out_path}")


if __name__ == "__main__":
    build_board()
