#!/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
"""
KEAVY-RELAY16 REV 2.0 (96.0 x 72.0 mm — fits SZOMK AK-P-01 115x90x40 PLC Box & UM72 DIN-Rail)
Full 2500Vrms Galvanically Isolated 16-Channel 24VDC NPN Relay Driver:
- Bus Domain (GND_BUS, +5V_BUS, +3V3_BUS): DC3-10P left/right pass-through + USBLC6-2SC6 ESD + B0505S-1W Primary + ADuM1250ARZ Side 1
- Isolated Domain (GND_ISO = 24V GND, +5V_ISO -> AMS1117-3.3 -> +3V3_ISO):
  * ZERO electrical ground connection between KEAVY-BUS and 24V stage (0% ground loop!)
  * ADuM1250ARZ Side 2 + 4.7k local pull-ups + MCP23017 (SW1 0x20-0x27) + 2x ULN2803G + 16x LEDs + 3.81mm terminals
"""

import os
import sys
import pcbnew

PRJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PRJ_DIR))
from keavy_common import *

BOARD_W = 96.0


def build_board():
    board = pcbnew.BOARD()
    add_board_outline(board, BOARD_W)

    # Bus Domain Nets (Galvanically Isolated from 24V stage!)
    net_gnd_bus = add_net(board, "GND_BUS")
    net_5v_bus = add_net(board, "+5V_BUS")
    net_3v3_bus = add_net(board, "+3V3_BUS")
    net_sda_bus = add_net(board, "I2C_SDA")
    net_scl_bus = add_net(board, "I2C_SCL")
    net_bus_int = add_net(board, "BUS_INT")

    # Isolated 24V & Local Logic Domain Nets
    net_gnd_iso = add_net(board, "GND_ISO")
    net_24v_bus = add_net(board, "+24V_BUS")
    net_5v_iso = add_net(board, "+5V_ISO")
    net_3v3_iso = add_net(board, "+3V3_ISO")
    net_sda_iso = add_net(board, "ISO_SDA")
    net_scl_iso = add_net(board, "ISO_SCL")
    net_addr = [add_net(board, f"ADDR_A{i}") for i in range(3)]
    net_ctrl = [add_net(board, f"RELAY_CH{i}") for i in range(1, 17)]
    net_out = [add_net(board, f"CH{i}_NPN_OUT") for i in range(1, 17)]
    net_led = [add_net(board, f"LED_CH{i}_A") for i in range(1, 17)]

    add_mounting_holes(board, BOARD_W, net_gnd_iso)

    # KEAVY-BUS Left & Right Shrouded IDC Box Headers (DC3-10P)
    j_in = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_IN", "DC3-10P", 5.5, BUS_Y, ref_offset=(1.2, -7.2), val_offset=(1.2, 17.2))
    assign_keavy_bus_nets(j_in, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_in)

    j_out = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_OUT", "DC3-10P", BOARD_W - 7.5, BUS_Y, ref_offset=(0.5, -7.2), val_offset=(0.5, 17.2))
    assign_keavy_bus_nets(j_out, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_out)

    # Top-Facing 24V Input + Protection + Address DIP Switch (Isolated Domain)
    j1 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal", "J1", "24V_IN", 22.0, 7.5, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(j1, "1", net_24v_bus); set_pad_net(j1, "2", net_gnd_iso); board.Add(j1)
    j1_p1, j1_p2 = pad_xy(j1, "1"), pad_xy(j1, "2")
    add_silk_text(board, "+24V", j1_p1[0], 15.2, size_mm=0.85, bold=True)
    add_silk_text(board, "-GND", j1_p2[0], 15.2, size_mm=0.85, bold=True)

    d_tvs = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SMB", "D_TVS", "SMBJ28A", 33.5, 9.0, ref_offset=(0.0, -3.1), val_offset=(0.0, 3.1))
    set_pad_net(d_tvs, "1", net_24v_bus); set_pad_net(d_tvs, "2", net_gnd_iso); board.Add(d_tvs)

    # Rule #9: High-frequency ceramic EMI bypass cap right at 24V input
    c1_hf = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C1_HF", "100nF 50V", 38.5, 9.0, angle=90.0, show_val=False, ref_offset=(0.0, -2.5))
    set_pad_net(c1_hf, "1", net_24v_bus); set_pad_net(c1_hf, "2", net_gnd_iso); board.Add(c1_hf)

    c1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_THT.pretty", "CP_Radial_D6.3mm_P2.50mm", "C1", "100uF 35V", 43.0, 8.5, ref_offset=(1.25, -4.5), val_offset=(1.25, 4.5))
    set_pad_net(c1, "1", net_24v_bus); set_pad_net(c1, "2", net_gnd_iso); board.Add(c1)

    sw1 = load_fp(f"{KICAD_FP_DIR}/Button_Switch_SMD.pretty", "SW_DIP_SPSTx03_Slide_6.7x9.18mm_W8.61mm_P2.54mm_LowProfile", "SW1", "ADDR 0x20-27", 57.0, 10.0, ref_offset=(0.0, -6.0), val_offset=(0.0, 6.0))
    set_pad_net(sw1, ["1", "2", "3"], net_3v3_iso)
    set_pad_net(sw1, "6", net_addr[0]); set_pad_net(sw1, "5", net_addr[1]); set_pad_net(sw1, "4", net_addr[2])
    board.Add(sw1)
    add_silk_text(board, "A0", 50.0, 7.46, size_mm=0.8, bold=True)
    add_silk_text(board, "A1", 50.0, 10.00, size_mm=0.8, bold=True)
    add_silk_text(board, "A2", 50.0, 12.54, size_mm=0.8, bold=True)

    r_addr = []
    for i, pad_n in enumerate(["6", "5", "4"]):
        swp = pad_xy(sw1, pad_n)
        ra = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RA{i}", "10k", 65.5, swp[1], show_ref=False, show_val=False)
        set_pad_net(ra, "1", net_addr[i]); set_pad_net(ra, "2", net_gnd_iso); board.Add(ra)
        r_addr.append(ra)
    add_silk_text(board, "RA0-2 10k", 66.5, 4.8, size_mm=0.8)

    add_silk_text(board, "KEAVY-RELAY16 V2", 79.5, 7.5, size_mm=0.8, bold=True)
    add_silk_text(board, "2500V ISO | 0x20-27", 79.5, 10.0, size_mm=0.8)
    add_silk_text(board, "AK-P-01 / UM72", 79.5, 12.5, size_mm=0.8)

    # REV 2.0 Galvanic Isolation Stage: B0505S-1W + AMS1117-3.3 + ADuM1250ARZ + 4.7k Local Pull-ups
    # Placed cleanly in the open left-upper zone (x=16..42, y=24..37) above U5!
    u_dcdc = load_fp(f"{KICAD_FP_DIR}/Converter_DCDC.pretty", "Converter_DCDC_Murata_MEE1SxxxxSC_THT", "U_DCDC", "B0505S-1W", 17.5, 24.5, angle=0.0, ref_offset=(2.0, -4.6), val_offset=(2.0, -3.3))
    set_pad_net(u_dcdc, "1", net_gnd_bus)
    set_pad_net(u_dcdc, "2", net_5v_bus)
    set_pad_net(u_dcdc, "3", net_gnd_iso)
    set_pad_net(u_dcdc, "4", net_5v_iso)
    board.Add(u_dcdc)

    u_ldo = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", "U_LDO", "AMS1117-3.3", 28.5, 31.5, angle=0.0, ref_offset=(0.0, -5.8), val_offset=(0.0, -4.5))
    set_pad_net(u_ldo, "1", net_gnd_iso); set_pad_net(u_ldo, ["2", "4"], net_3v3_iso); set_pad_net(u_ldo, "3", net_5v_iso); board.Add(u_ldo)

    c_l1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_L1", "10uF", 21.5, 36.2, ref_offset=(-4.2, -0.5), val_offset=(-4.2, 0.8))
    set_pad_net(c_l1, "1", net_5v_iso); set_pad_net(c_l1, "2", net_gnd_iso); board.Add(c_l1)

    c_l2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_L2", "10uF", 34.0, 34.8, angle=90.0, show_ref=False, show_val=False)
    set_pad_net(c_l2, "1", net_3v3_iso); set_pad_net(c_l2, "2", net_gnd_iso); board.Add(c_l2)
    add_silk_text(board, "C_L2 10u", 28.5, 36.6, size_mm=0.8)

    # ADuM1250ARZ (SOIC-8, rotated -90 deg: Pins 4..1 Bus Side on TOP, Pins 5..8 Isolated Side on BOTTOM!)
    u_iso = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-8_3.9x4.9mm_P1.27mm", "U_ISO", "ADuM1250ARZ", 36.5, 26.5, angle=-90.0, ref_offset=(0.0, -5.7), val_offset=(0.0, -4.4))
    set_pad_net(u_iso, "1", net_3v3_bus)
    set_pad_net(u_iso, "2", net_sda_bus)
    set_pad_net(u_iso, "3", net_scl_bus)
    set_pad_net(u_iso, "4", net_gnd_bus)
    set_pad_net(u_iso, "5", net_gnd_iso)
    set_pad_net(u_iso, "6", net_scl_iso)
    set_pad_net(u_iso, "7", net_sda_iso)
    set_pad_net(u_iso, "8", net_3v3_iso)
    board.Add(u_iso)

    # Datasheet Mandatory 100nF Ceramic Bypass Caps directly on ADuM1250ARZ Side 1 (Bus) & Side 2 (Iso)
    # Note: U_ISO angle=-90 -> Top: Pin 4(GND_BUS) left x=34.6, Pin 1(+3V3_BUS) right x=38.4
    #                          Bottom: Pin 5(GND_ISO) left x=34.6, Pin 8(+3V3_ISO) right x=38.4
    c_iso1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_ISO1", "100nF", 31.2, 23.9, angle=180.0, show_val=False, ref_offset=(-3.6, 0.0))
    set_pad_net(c_iso1, "1", net_gnd_bus); set_pad_net(c_iso1, "2", net_3v3_bus); board.Add(c_iso1)

    c_iso2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_ISO2", "100nF", 41.2, 28.9, angle=90.0, show_ref=False, show_val=False)
    set_pad_net(c_iso2, "1", net_3v3_iso); set_pad_net(c_iso2, "2", net_gnd_iso); board.Add(c_iso2)

    r_isda = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_ISDA", "4.7k", 41.0, 33.5, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(r_isda, "1", net_3v3_iso); set_pad_net(r_isda, "2", net_sda_iso); board.Add(r_isda)

    r_iscl = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_ISCL", "4.7k", 41.0, 35.8, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(r_iscl, "1", net_3v3_iso); set_pad_net(r_iscl, "2", net_scl_iso); board.Add(r_iscl)
    add_silk_text(board, "4.7k", 41.0, 31.6, size_mm=0.8)

    # MCP23017 (U7) + 2x ULN2803G (U5, U6) — Isolated Domain
    u7 = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-28W_7.5x17.9mm_P1.27mm", "U7", "MCP23017", 51.0, 32.0, ref_offset=(0.0, -10.2), val_offset=(0.0, 10.2))
    for i in range(8):
        set_pad_net(u7, str(i + 1), net_ctrl[i])
        set_pad_net(u7, str(21 + i), net_ctrl[8 + i])
    set_pad_net(u7, ["9", "18"], net_3v3_iso)  # VDD & ~RESET tied to +3V3_ISO
    set_pad_net(u7, "10", net_gnd_iso)
    set_pad_net(u7, "12", net_scl_iso); set_pad_net(u7, "13", net_sda_iso)
    set_pad_net(u7, "15", net_addr[0]); set_pad_net(u7, "16", net_addr[1]); set_pad_net(u7, "17", net_addr[2])
    board.Add(u7)

    c_io = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_IO", "100nF", 43.0, 38.5, show_ref=False, show_val=False)
    set_pad_net(c_io, "1", net_3v3_iso); set_pad_net(c_io, "2", net_gnd_iso); board.Add(c_io)
    add_silk_text(board, "C_IO", 42.5, 41.2, size_mm=0.8)
    add_silk_text(board, "100n", 42.5, 42.5, size_mm=0.8)

    u5 = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-18W_7.5x11.6mm_P1.27mm", "U5", "ULN2803G", 32.0, 44.0, angle=-90.0, ref_offset=(-9.2, -1.2), val_offset=(-9.2, 1.2))
    for i in range(8): set_pad_net(u5, str(8 - i), net_ctrl[i]); set_pad_net(u5, str(11 + i), net_out[i])
    set_pad_net(u5, "9", net_gnd_iso); set_pad_net(u5, "10", net_24v_bus); board.Add(u5)

    u6 = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-18W_7.5x11.6mm_P1.27mm", "U6", "ULN2803G", 68.0, 44.0, angle=-90.0, ref_offset=(9.2, -1.2), val_offset=(9.2, 1.2))
    for i in range(8): set_pad_net(u6, str(8 - i), net_ctrl[8 + i]); set_pad_net(u6, str(11 + i), net_out[8 + i])
    set_pad_net(u6, "9", net_gnd_iso); set_pad_net(u6, "10", net_24v_bus); board.Add(u6)

    # Bottom-Facing 3.81mm Screw Terminals + 16x LEDs
    j2 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1-2-3.81_1x02_P3.81mm_Horizontal", "J2", "24V_OUT", 13.0, 66.5, show_ref=False, show_val=False)
    set_pad_net(j2, "1", net_24v_bus); set_pad_net(j2, "2", net_gnd_iso); board.Add(j2)

    j3 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1-8-3.81_1x08_P3.81mm_Horizontal", "J3", "CH1-CH8", 22.0, 66.5, show_ref=False, show_val=False)
    for i in range(8): set_pad_net(j3, str(i + 1), net_out[i])
    board.Add(j3)

    j4 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1-8-3.81_1x08_P3.81mm_Horizontal", "J4", "CH9-CH16", 55.5, 66.5, show_ref=False, show_val=False)
    for i in range(8): set_pad_net(j4, str(i + 1), net_out[8 + i])
    board.Add(j4)

    j2_p1, j2_p2 = pad_xy(j2, "1"), pad_xy(j2, "2")
    add_silk_text(board, "PWR", (j2_p1[0] + j2_p2[0]) / 2.0, 58.6, size_mm=0.8, bold=True)
    add_silk_text(board, "+", j2_p1[0], 60.6, size_mm=0.95, bold=True)
    add_silk_text(board, "-", j2_p2[0], 60.6, size_mm=0.95, bold=True)
    add_silk_text(board, "RL 10k", 15.8, 54.4, size_mm=0.8)
    add_silk_text(board, "LED", 15.8, 56.8, size_mm=0.8)

    ch_term_pads = [pad_xy(j3, str(i + 1)) for i in range(8)] + [pad_xy(j4, str(i + 1)) for i in range(8)]
    rl_parts, led_parts = [], []
    for idx, (tx, ty) in enumerate(ch_term_pads):
        ch = idx + 1
        r_led = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RL{ch}", "10k", tx, 54.4, angle=-90.0, show_ref=False, show_val=False)
        set_pad_net(r_led, "1", net_24v_bus); set_pad_net(r_led, "2", net_led[idx]); board.Add(r_led)
        led = load_fp(f"{KICAD_FP_DIR}/LED_SMD.pretty", "LED_0805_2012Metric", f"LED{ch}", "LED", tx, 58.1, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(led, "2", net_led[idx]); set_pad_net(led, "1", net_out[idx]); board.Add(led)
        add_silk_text(board, f"{ch}", tx, 60.6, size_mm=0.8, bold=True)
        add_silk_text(board, f"{ch}", tx, 63.2, size_mm=0.95, bold=True, layer=pcbnew.B_SilkS)
        rl_parts.append(r_led); led_parts.append(led)

    # KEAVY-BUS Pass-Through Trunk on B.Cu along y = 17.4..21.65 (100% Bus Domain!)
    ty = route_bus_trunk(board, j_in, j_out, BOARD_W, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int, y_start=17.4)

    # Tap Bus Domain -> B0505S-1W Primary (1=GND_BUS, 2=+5V_BUS) & ADuM1250ARZ Side 1 (1=3V3, 2=SDA, 3=SCL, 4=GND)
    dc1, dc2, dc3, dc4 = [pad_xy(u_dcdc, str(k)) for k in range(1, 5)]
    add_via(board, dc1[0] - 1.8, ty["gnd"], net_gnd_bus, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [(dc1[0] - 1.8, ty["gnd"]), (dc1[0] - 1.8, dc1[1]), dc1], 0.45, pcbnew.F_Cu, net_gnd_bus)
    add_via(board, dc2[0] + 1.9, ty["5v"], net_5v_bus, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [(dc2[0] + 1.9, ty["5v"]), (dc2[0] + 1.9, dc2[1]), dc2], 0.45, pcbnew.F_Cu, net_5v_bus)

    iso_p = [pad_xy(u_iso, str(k)) for k in range(1, 9)]  # 0..3 = Bus Side (top), 4..7 = Iso Side (bottom)
    for idx_p, (snet, t_key) in enumerate([(net_3v3_bus, "3v3"), (net_sda_bus, "sda"), (net_scl_bus, "scl"), (net_gnd_bus, "gnd")]):
        ip = iso_p[idx_p]
        add_via(board, ip[0], ty[t_key], snet, dia_mm=0.60, drill_mm=0.30)
        add_track(board, ip[0], ty[t_key], ip[0], ip[1], 0.22, pcbnew.F_Cu, snet)

    # Route C_ISO1 (100nF Bus Side) & C_ISO2 (100nF Iso Side) right at U_ISO pads (zero crossings!)
    ci1_p1, ci1_p2 = pad_xy(c_iso1, "1"), pad_xy(c_iso1, "2")
    add_track(board, ci1_p1[0], ci1_p1[1], iso_p[3][0], iso_p[3][1], 0.25, pcbnew.F_Cu, net_gnd_bus)
    add_via(board, ci1_p2[0], ty["3v3"], net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, ci1_p2[0], ci1_p2[1], ci1_p2[0], ty["3v3"], 0.25, pcbnew.F_Cu, net_3v3_bus)

    ci2_p1, ci2_p2 = pad_xy(c_iso2, "1"), pad_xy(c_iso2, "2")
    add_route(board, [ci2_p1, (ci2_p1[0], 30.2), (pad_xy(r_isda, "1")[0], 30.2)], 0.25, pcbnew.F_Cu, net_3v3_iso, chamfer=False)
    add_route(board, [ci2_p2, (ci2_p2[0], 26.2), (iso_p[4][0], 26.2), iso_p[4]], 0.25, pcbnew.F_Cu, net_gnd_iso, chamfer=False)

    # Isolated Power Routing: B0505S-1W (3=GND_ISO, 4=+5V_ISO) -> C_L1 -> U_LDO -> C_L2 -> +3V3_ISO
    ul_gnd, ul_out, ul_tab, ul_in = pad_xy(u_ldo, "1"), pad_xy(u_ldo, "2"), pad_xy(u_ldo, "2", "max_x"), pad_xy(u_ldo, "3")
    cl1_p1, cl1_p2 = pad_xy(c_l1, "1"), pad_xy(c_l1, "2")
    cl2_p1, cl2_p2 = pad_xy(c_l2, "1"), pad_xy(c_l2, "2")
    add_route(board, [dc4, (dc4[0], cl1_p1[1]), cl1_p1], 0.45, pcbnew.F_Cu, net_5v_iso)
    add_route(board, [cl1_p1, (cl1_p1[0], ul_in[1]), ul_in], 0.45, pcbnew.F_Cu, net_5v_iso)
    # Tie local GND_ISO pads (dc3, ul_gnd, cl1_p2, cl2_p2, iso_p[4]) directly to open B.Cu GND_ISO plane (left of U5!)
    add_route(board, [dc3, (dc3[0] + 3.0, dc3[1]), (dc3[0] + 3.0, ul_gnd[1]), ul_gnd], 0.35, pcbnew.F_Cu, net_gnd_iso)
    add_route(board, [dc3, (dc3[0] - 1.8, dc3[1]), (dc3[0] - 1.8, 38.0), (cl1_p2[0], 38.0), cl1_p2], 0.35, pcbnew.F_Cu, net_gnd_iso)
    add_via(board, cl1_p2[0], 38.0, net_gnd_iso, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [iso_p[4], (iso_p[4][0], 29.0), (ul_gnd[0], 29.0), ul_gnd], 0.25, pcbnew.F_Cu, net_gnd_iso)
    add_route(board, [cl2_p2, (cl2_p2[0], 32.0), (34.6, 32.0), (34.6, 29.0)], 0.25, pcbnew.F_Cu, net_gnd_iso)

    add_track(board, ul_out[0], ul_out[1], ul_tab[0], ul_tab[1], 0.7, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [ul_tab, (ul_tab[0], cl2_p1[1]), cl2_p1], 0.4, pcbnew.F_Cu, net_3v3_iso)

    # Isolated +3V3_ISO & I2C (ADuM1250 Side 2 -> R_ISDA/R_ISCL -> U7 MCP23017 & SW1)
    risda_p1, risda_p2 = pad_xy(r_isda, "1"), pad_xy(r_isda, "2")
    riscl_p1, riscl_p2 = pad_xy(r_iscl, "1"), pad_xy(r_iscl, "2")
    cio_p1, cio_p2 = pad_xy(c_io, "1"), pad_xy(c_io, "2")
    u7_vdd, u7_vss, u7_scl, u7_sda, u7_rst = pad_xy(u7, "9"), pad_xy(u7, "10"), pad_xy(u7, "12"), pad_xy(u7, "13"), pad_xy(u7, "18")

    # +3V3_ISO 100% on F.Cu across cl2_p1 -> cio_p1 -> riscl_p1 -> risda_p1 -> iso_p[7]!
    add_route(board, [cl2_p1, (cl2_p1[0], 37.3), (cio_p1[0], 37.3), cio_p1], 0.35, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [iso_p[7], (iso_p[7][0], 30.2), (risda_p1[0], 30.2), risda_p1, riscl_p1, (riscl_p1[0], 37.3), (cio_p1[0], 37.3)], 0.28, pcbnew.F_Cu, net_3v3_iso)
    add_gnd_via_near(board, cio_p2[0], cio_p2[1], 0.0, 1.5, net_gnd_iso)

    # +3V3_ISO via B.Cu from C_IO(1) -> U7(9), U7(18), and SW1(1,2,3)
    add_via(board, cio_p1[0], cio_p1[1] - 1.5, net_3v3_iso, dia_mm=0.65, drill_mm=0.35)
    add_track(board, cio_p1[0], cio_p1[1], cio_p1[0], cio_p1[1] - 1.5, 0.3, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [(cio_p1[0], cio_p1[1] - 1.5), (49.0, cio_p1[1] - 1.5), (49.0, u7_vdd[1])], 0.3, pcbnew.B_Cu, net_3v3_iso)
    add_via(board, 49.0, u7_vdd[1], net_3v3_iso, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [(49.0, u7_vdd[1]), u7_vdd], 0.25, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [(49.0, u7_vdd[1]), (49.0, u7_rst[1]), u7_rst], 0.25, pcbnew.F_Cu, net_3v3_iso)
    sw_p1, sw_p3 = pad_xy(sw1, "1"), pad_xy(sw1, "3")
    add_track(board, sw_p1[0], sw_p1[1], sw_p3[0], sw_p3[1], 0.35, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [(49.0, u7_vdd[1]), (52.7, u7_vdd[1]), (52.7, sw_p3[1])], 0.3, pcbnew.F_Cu, net_3v3_iso)

    add_gnd_via_near(board, u7_vss[0], u7_vss[1], -1.5, 0.0, net_gnd_iso)

    # ISO_SDA & ISO_SCL: ADuM1250(7,6) -> R_ISDA(2)/R_ISCL(2) on F.Cu, then B.Cu (below RELAY_CH8 y=32.6!) -> U7(13,12)
    add_route(board, [iso_p[6], (iso_p[6][0], risda_p2[1]), risda_p2], 0.22, pcbnew.F_Cu, net_sda_iso)
    add_via(board, risda_p2[0] - 2.0, risda_p2[1], net_sda_iso, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [(risda_p2[0] - 2.0, risda_p2[1]), (risda_p2[0] - 2.0, u7_sda[1]), (45.2, u7_sda[1])], 0.22, pcbnew.B_Cu, net_sda_iso)
    add_via(board, 45.2, u7_sda[1], net_sda_iso, dia_mm=0.60, drill_mm=0.30)
    add_track(board, 45.2, u7_sda[1], u7_sda[0], u7_sda[1], 0.22, pcbnew.F_Cu, net_sda_iso)

    add_route(board, [iso_p[5], (iso_p[5][0], riscl_p2[1]), riscl_p2], 0.22, pcbnew.F_Cu, net_scl_iso)
    add_via(board, riscl_p2[0] - 1.2, riscl_p2[1], net_scl_iso, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [(riscl_p2[0] - 1.2, riscl_p2[1]), (riscl_p2[0] - 1.2, u7_scl[1]), (45.2, u7_scl[1])], 0.22, pcbnew.B_Cu, net_scl_iso)
    add_via(board, 45.2, u7_scl[1], net_scl_iso, dia_mm=0.60, drill_mm=0.30)
    add_track(board, 45.2, u7_scl[1], u7_scl[0], u7_scl[1], 0.22, pcbnew.F_Cu, net_scl_iso)

    # DIP Switch A0..A2 -> RA0..RA2 -> U7 Pins 15,16,17
    for i, (sw_pn, u7_pn) in enumerate([("6", "15"), ("5", "16"), ("4", "17")]):
        swp = pad_xy(sw1, sw_pn)
        rap1, rap2 = pad_xy(r_addr[i], "1"), pad_xy(r_addr[i], "2")
        u7a = pad_xy(u7, u7_pn)
        add_track(board, swp[0], swp[1], rap1[0], rap1[1], 0.22, pcbnew.F_Cu, net_addr[i])
        add_gnd_via_near(board, rap2[0], rap2[1], 1.5, 0.0, net_gnd_iso)
        bx = 63.2 - i * 0.72
        by = 15.94 - i * 0.72
        ax = 58.0 + i * 0.85
        add_via(board, bx, swp[1], net_addr[i], dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(bx, swp[1]), (bx, by), (ax, by)], 0.20, pcbnew.B_Cu, net_addr[i])
        add_via(board, ax, by, net_addr[i], dia_mm=0.60, drill_mm=0.30)
        add_track(board, ax, by, ax, 22.4, 0.20, pcbnew.F_Cu, net_addr[i])
        add_via(board, ax, 22.4, net_addr[i], dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(ax, 22.4), (ax, u7a[1])], 0.20, pcbnew.B_Cu, net_addr[i])
        add_via(board, ax, u7a[1], net_addr[i], dia_mm=0.60, drill_mm=0.30)
        add_track(board, ax, u7a[1], u7a[0], u7a[1], 0.20, pcbnew.F_Cu, net_addr[i])

    # MCP23017 -> U5 (CH1-8) via B.Cu (clears U_LDO/U_ISO cleanly!) & U6 (CH9-16) 100% on F.Cu
    for i in range(8):
        # Right bank (CH9-16) straight on F.Cu
        p_io_r, p_dr_r = pad_xy(u7, str(21 + i)), pad_xy(u6, str(8 - i))
        add_route(board, [p_io_r, (p_dr_r[0], p_io_r[1]), p_dr_r], 0.20, pcbnew.F_Cu, net_ctrl[8 + i])
        # Left bank (CH1-8) drop via left of U7 -> B.Cu cleanly under U_LDO -> via up at U5 top pins!
        p_io_l, p_dr_l = pad_xy(u7, str(i + 1)), pad_xy(u5, str(8 - i))
        vx_u7 = 44.8 - (i % 2) * 0.9
        add_track(board, p_io_l[0], p_io_l[1], vx_u7, p_io_l[1], 0.20, pcbnew.F_Cu, net_ctrl[i])
        add_via(board, vx_u7, p_io_l[1], net_ctrl[i], dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(vx_u7, p_io_l[1]), (p_dr_l[0], p_io_l[1]), (p_dr_l[0], 38.0)], 0.20, pcbnew.B_Cu, net_ctrl[i])
        add_via(board, p_dr_l[0], 38.0, net_ctrl[i], dia_mm=0.60, drill_mm=0.30)
        add_track(board, p_dr_l[0], 38.0, p_dr_l[0], p_dr_l[1], 0.20, pcbnew.F_Cu, net_ctrl[i])

    rl_top_y = pad_xy(rl_parts[0], "1")[1]
    for u_drv in (u5, u6):
        ug = pad_xy(u_drv, "9"); add_gnd_via_near(board, ug[0], ug[1], -1.8, 0.0, net_gnd_iso, trace_w=0.5)
        uc = pad_xy(u_drv, "10"); add_route(board, [uc, (uc[0] - 1.8, uc[1]), (uc[0] - 1.8, rl_top_y)], 0.6, pcbnew.F_Cu, net_24v_bus)

    # U5/U6 Outputs -> 3.81mm Terminals (B.Cu) & LEDs (F.Cu)
    for bank, u_drv in enumerate((u5, u6)):
        for local_i in range(8):
            idx = bank * 8 + local_i
            u_out = pad_xy(u_drv, str(11 + local_i))
            term_xy = ch_term_pads[idx]
            rl_p2 = pad_xy(rl_parts[idx], "2")
            led_p1, led_p2 = pad_xy(led_parts[idx], "1"), pad_xy(led_parts[idx], "2")
            step = (local_i if local_i < 3 else (7 - local_i)) if bank == 0 else (local_i if local_i < 4 else (7 - local_i))
            vy = 49.7 + step * 0.65
            add_track(board, u_out[0], u_out[1], u_out[0], vy, 0.22, pcbnew.F_Cu, net_out[idx])
            add_via(board, u_out[0], vy, net_out[idx], dia_mm=0.60, drill_mm=0.30)
            add_route(board, [(u_out[0], vy), (term_xy[0], vy), term_xy], 0.28, pcbnew.B_Cu, net_out[idx])
            add_track(board, rl_p2[0], rl_p2[1], led_p2[0], led_p2[1], 0.25, pcbnew.F_Cu, net_led[idx])
            add_track(board, led_p1[0], led_p1[1], term_xy[0], term_xy[1], 0.28, pcbnew.F_Cu, net_out[idx])

    # +24V_BUS Feeder
    dtvs_p1, dtvs_p2 = pad_xy(d_tvs, "1"), pad_xy(d_tvs, "2")
    c1_p1 = pad_xy(c1, "1")
    c1hf_p1, c1hf_p2 = pad_xy(c1_hf, "1"), pad_xy(c1_hf, "2")
    add_route(board, [j1_p1, (j1_p1[0], 12.8), (dtvs_p1[0], 12.8), dtvs_p1], 1.5, pcbnew.F_Cu, net_24v_bus)
    add_route(board, [(dtvs_p1[0], 12.8), (c1_p1[0], 12.8), c1_p1], 1.5, pcbnew.F_Cu, net_24v_bus)
    add_track(board, c1hf_p1[0], c1hf_p1[1], c1hf_p1[0], 12.8, 0.5, pcbnew.F_Cu, net_24v_bus)
    add_gnd_via_near(board, c1hf_p2[0], c1hf_p2[1], 0.0, -1.4, net_gnd_iso)
    add_gnd_via_near(board, dtvs_p2[0], dtvs_p2[1], 1.8, 0.0, net_gnd_iso)
    add_route(board, [(j1_p1[0], 12.8), (13.0, 12.8), (13.0, rl_top_y), j2_p1], 1.5, pcbnew.F_Cu, net_24v_bus)
    add_route(board, [(13.0, rl_top_y), (pad_xy(rl_parts[-1], "1")[0], rl_top_y)], 1.0, pcbnew.F_Cu, net_24v_bus)

    # Rule #11: True 2500 Vrms Galvanic Isolation Moat — block GND_ISO pour from Bus Domain & under isolation barrier!
    add_zone_keepout(board, [(0.0, 24.0), (12.5, 24.0), (12.5, 48.0), (0.0, 48.0)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(BOARD_W - 12.5, 24.0), (BOARD_W, 24.0), (BOARD_W, 48.0), (BOARD_W - 12.5, 48.0)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(8.0, 16.0), (BOARD_W - 8.0, 16.0), (BOARD_W - 8.0, 23.0), (8.0, 23.0)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(14.5, 22.5), (21.3, 22.5), (21.3, 27.5), (14.5, 27.5)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(29.0, 22.5), (39.5, 22.5), (39.5, 27.4), (29.0, 27.4)], layers=(pcbnew.B_Cu,))

    # Bridge top & bottom GND_ISO zones on F.Cu (cleanly over FR4 dielectric at x=74.5, away from Bus pads)
    add_via(board, 74.5, 14.5, net_gnd_iso, dia_mm=0.9, drill_mm=0.45)
    add_via(board, 74.5, 24.5, net_gnd_iso, dia_mm=0.9, drill_mm=0.45)
    add_track(board, 74.5, 14.5, 74.5, 24.5, 1.5, pcbnew.F_Cu, net_gnd_iso)

    # Rule #4: Perimeter Ground Stitching Vias (Isolated Domain only, skipping Bus connectors)
    add_perimeter_gnd_stitching(board, BOARD_W, net_gnd_iso, skip_boxes=[(0.0, 15.0, 15.0, 50.0), (BOARD_W - 15.0, 15.0, BOARD_W, 50.0)])

    # Isolated B.Cu GND_ISO Plane
    add_zone(board, net_gnd_iso, pcbnew.B_Cu, [(1.0, 1.0), (BOARD_W - 1.0, 1.0), (BOARD_W - 1.0, BOARD_H - 1.0), (1.0, BOARD_H - 1.0)], priority=0, clearance_mm=0.4)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_path = os.path.join(PRJ_DIR, "keavy_relay16.kicad_pcb")
    board.Save(out_path)
    print(f"Successfully generated: {out_path}")


if __name__ == "__main__":
    build_board()
