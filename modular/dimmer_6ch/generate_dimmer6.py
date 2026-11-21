#!/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
"""
KEAVY-DIMMER6 REV 2.0 (96.0 x 72.0 mm — fits SZOMK AK-P-01 115x90x40 PLC Box & UM72 DIN-Rail)
Full 2500Vrms Galvanically Isolated 6-Channel 60W/CH 24V LED Dimmer:
- Bus Domain (GND_BUS, +5V_BUS, +3V3_BUS): DC3-10P left/right pass-through + B0505S-1W Primary + ADuM1250ARZ Side 1
- Isolated Domain (GND_ISO = 15A 24V Power GND, +5V_ISO -> AMS1117-3.3 -> +3V3_ISO):
  * ZERO electrical ground connection between KEAVY-BUS and 15A 24V Dimmer stage (0% ground loop!)
  * ADuM1250ARZ Side 2 + 4.7k local pull-ups + PCA9685PW (SW1 0x40-0x47) + 6x AOD4184A + 6x SS34 + 6x LEDs
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

    # Bus Domain Nets (Galvanically Isolated from 15A 24V Dimmer stage!)
    net_gnd_bus = add_net(board, "GND_BUS")
    net_5v_bus = add_net(board, "+5V_BUS")
    net_3v3_bus = add_net(board, "+3V3_BUS")
    net_sda_bus = add_net(board, "I2C_SDA")
    net_scl_bus = add_net(board, "I2C_SCL")
    net_bus_int = add_net(board, "BUS_INT")

    # Isolated 24V & Local Logic Domain Nets
    net_gnd_iso = add_net(board, "GND_ISO")
    net_24v_in = add_net(board, "+24V_IN")
    net_24v_fused = add_net(board, "+24V_FUSED")
    net_24v_bus = add_net(board, "+24V_BUS")
    net_rev_gate = add_net(board, "REV_GATE")
    net_5v_iso = add_net(board, "+5V_ISO")
    net_3v3_iso = add_net(board, "+3V3_ISO")
    net_sda_iso = add_net(board, "ISO_SDA")
    net_scl_iso = add_net(board, "ISO_SCL")
    net_addr = [add_net(board, f"ADDR_A{i}") for i in range(3)]

    net_pwm = [add_net(board, f"PWM_CH{i}") for i in range(1, 7)]
    net_gate = [add_net(board, f"GATE_CH{i}") for i in range(1, 7)]
    net_out = [add_net(board, f"CH{i}_OUT-") for i in range(1, 7)]
    net_led = [add_net(board, f"LED_CH{i}_A") for i in range(1, 7)]

    add_mounting_holes(board, BOARD_W, net_gnd_iso)

    # KEAVY-BUS Left & Right Shrouded IDC Box Headers (DC3-10P)
    j_in = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_IN", "DC3-10P", 5.5, BUS_Y, ref_offset=(1.2, -7.2), val_offset=(1.2, 17.2))
    assign_keavy_bus_nets(j_in, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_in)

    j_out = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_OUT", "DC3-10P", BOARD_W - 7.5, BUS_Y, ref_offset=(0.5, -7.2), val_offset=(0.5, 17.2))
    assign_keavy_bus_nets(j_out, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_out)

    # Top-Facing High-Current 24V Input & Protection (Isolated Domain)
    j1 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal", "J1", "24V_IN", 19.0, 7.5, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(j1, "1", net_24v_in); set_pad_net(j1, "2", net_gnd_iso); board.Add(j1)
    j1_p1, j1_p2 = pad_xy(j1, "1"), pad_xy(j1, "2")
    add_silk_text(board, "+24V", j1_p1[0], 15.2, size_mm=0.85, bold=True)
    add_silk_text(board, "-GND", j1_p2[0], 15.2, size_mm=0.85, bold=True)

    f1 = load_fp(f"{KICAD_FP_DIR}/Fuse.pretty", "Fuseholder_Blade_Mini_Keystone_3568", "F1", "15A FUSE", 27.0, 6.0, ref_offset=(4.96, -3.5), val_offset=(4.96, 6.5))
    set_pad_net(f1, "1", net_24v_in); set_pad_net(f1, "2", net_24v_fused); board.Add(f1)

    q_rev = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "TO-252-3_TabPin2", "Q_REV", "AOD403", 48.0, 8.5, ref_offset=(0.0, -5.8), val_offset=(0.0, -4.6))
    set_pad_net(q_rev, "1", net_rev_gate); set_pad_net(q_rev, ["2", ""], net_24v_fused); set_pad_net(q_rev, "3", net_24v_bus); board.Add(q_rev)

    dz1 = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SOD-123", "DZ1", "BZT52C12", 42.0, 16.0, angle=180.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(dz1, "1", net_24v_bus); set_pad_net(dz1, "2", net_rev_gate); board.Add(dz1)

    r_rev = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_REV", "100k", 49.0, 16.0, ref_offset=(0.0, -1.8), val_offset=(0.0, 1.8))
    set_pad_net(r_rev, "1", net_rev_gate); set_pad_net(r_rev, "2", net_gnd_iso); board.Add(r_rev)

    c1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_THT.pretty", "CP_Radial_D10.0mm_P5.00mm", "C1", "470uF 35V", 56.5, 8.5, ref_offset=(2.5, -6.4), val_offset=(10.5, -2.0))
    set_pad_net(c1, "1", net_24v_bus); set_pad_net(c1, "2", net_gnd_iso); board.Add(c1)

    d_tvs = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SMB", "D_TVS", "SMBJ28A", 62.0, 17.0, ref_offset=(-6.2, 0.0), val_offset=(0.0, 3.0))
    set_pad_net(d_tvs, "1", net_24v_bus); set_pad_net(d_tvs, "2", net_gnd_iso); board.Add(d_tvs)

    c2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_1206_3216Metric", "C2", "10uF 50V", 72.0, 16.5, ref_offset=(0.0, -2.2), val_offset=(0.0, 2.2))
    set_pad_net(c2, "1", net_24v_bus); set_pad_net(c2, "2", net_gnd_iso); board.Add(c2)

    add_silk_text(board, "KEAVY-DIMMER6 V2", 79.5, 7.0, size_mm=0.8, bold=True)
    add_silk_text(board, "2500V ISO | 60W/CH", 79.5, 9.5, size_mm=0.8)
    add_silk_text(board, "AK-P-01 / UM72", 79.5, 12.0, size_mm=0.8)

    # REV 2.0 Galvanic Isolation Stage (cleanly placed right of PCA9685, x=56..79, y=26..37!)
    u_iso = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-8_3.9x4.9mm_P1.27mm", "U_ISO", "ADuM1250", 60.5, 28.5, angle=-90.0, ref_offset=(0.0, -5.5), val_offset=(0.0, -4.2))
    set_pad_net(u_iso, "1", net_3v3_bus); set_pad_net(u_iso, "2", net_sda_bus); set_pad_net(u_iso, "3", net_scl_bus); set_pad_net(u_iso, "4", net_gnd_bus)
    set_pad_net(u_iso, "5", net_gnd_iso); set_pad_net(u_iso, "6", net_scl_iso); set_pad_net(u_iso, "7", net_sda_iso); set_pad_net(u_iso, "8", net_3v3_iso)
    board.Add(u_iso)

    # Datasheet Mandatory 100nF Ceramic Bypass Caps directly on ADuM1250ARZ Side 1 (Bus) & Side 2 (Iso)
    # Note: U_ISO angle=-90 -> Top: Pin 4(GND_BUS) left x=58.6, Pin 1(+3V3_BUS) right x=62.4
    #                          Bottom: Pin 5(GND_ISO) left x=58.6, Pin 8(+3V3_ISO) right x=62.4
    c_iso1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_ISO1", "100nF", 65.0, 22.0, show_ref=False, show_val=False)
    set_pad_net(c_iso1, "1", net_3v3_bus); set_pad_net(c_iso1, "2", net_gnd_bus); board.Add(c_iso1)

    c_iso2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_ISO2", "100nF", 60.5, 35.0, show_ref=False, show_val=False)
    set_pad_net(c_iso2, "1", net_gnd_iso); set_pad_net(c_iso2, "2", net_3v3_iso); board.Add(c_iso2)

    u_dcdc = load_fp(f"{KICAD_FP_DIR}/Converter_DCDC.pretty", "Converter_DCDC_Murata_MEE1SxxxxSC_THT", "U_DCDC", "B0505S-1W", 74.5, 26.5, angle=0.0, ref_offset=(2.0, -4.5), val_offset=(2.0, -3.2))
    set_pad_net(u_dcdc, "1", net_gnd_bus); set_pad_net(u_dcdc, "2", net_5v_bus)
    set_pad_net(u_dcdc, "3", net_gnd_iso); set_pad_net(u_dcdc, "4", net_5v_iso)
    board.Add(u_dcdc)

    u_ldo = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", "U_LDO", "AMS1117-3.3", 67.8, 29.5, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(u_ldo, "1", net_gnd_iso); set_pad_net(u_ldo, ["2", "4"], net_3v3_iso); set_pad_net(u_ldo, "3", net_5v_iso); board.Add(u_ldo)
    add_silk_text(board, "U_LDO", 74.5, 37.2, size_mm=0.8)

    c_l1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_L1", "10uF", 69.2, 24.8, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(c_l1, "1", net_5v_iso); set_pad_net(c_l1, "2", net_gnd_iso); board.Add(c_l1)

    c_l2 = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_L2", "10uF", 66.0, 35.8, show_ref=False, show_val=False)
    set_pad_net(c_l2, "1", net_3v3_iso); set_pad_net(c_l2, "2", net_gnd_iso); board.Add(c_l2)
    add_silk_text(board, "C_L2 10u", 66.0, 38.0, size_mm=0.8)

    r_iscl = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_ISCL", "4.7k", 55.5, 26.8, angle=180.0, show_ref=False, val_offset=(0.0, -2.0))
    set_pad_net(r_iscl, "1", net_3v3_iso); set_pad_net(r_iscl, "2", net_scl_iso); board.Add(r_iscl)

    r_isda = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", "R_ISDA", "4.7k", 55.5, 29.8, angle=180.0, show_ref=False, val_offset=(0.0, 2.0))
    set_pad_net(r_isda, "1", net_3v3_iso); set_pad_net(r_isda, "2", net_sda_iso); board.Add(r_isda)

    # PCA9685PW (U1, TSSOP-28, angle=+90) — Isolated Domain
    u1 = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "TSSOP-28_4.4x9.7mm_P0.65mm", "U1", "PCA9685PW", 47.0, 28.5, angle=90.0, ref_offset=(0.0, -4.5), val_offset=(0.0, -5.8))
    set_pad_net(u1, "1", net_addr[0]); set_pad_net(u1, "2", net_addr[1]); set_pad_net(u1, "3", net_addr[2])
    set_pad_net(u1, ["4", "5", "14", "23", "24", "25"], net_gnd_iso)
    for i in range(6): set_pad_net(u1, str(6 + i), net_pwm[i])
    set_pad_net(u1, "26", net_scl_iso); set_pad_net(u1, "27", net_sda_iso); set_pad_net(u1, "28", net_3v3_iso)
    board.Add(u1)

    c_pwm = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_PWM", "100nF", 39.0, 27.5, angle=-90.0, ref_offset=(0.0, -3.5), val_offset=(0.0, 3.2))
    set_pad_net(c_pwm, "1", net_3v3_iso); set_pad_net(c_pwm, "2", net_gnd_iso); board.Add(c_pwm)

    # 3-Bit DIP Switch (Isolated Domain)
    sw1 = load_fp(f"{KICAD_FP_DIR}/Button_Switch_SMD.pretty", "SW_DIP_SPSTx03_Slide_6.7x9.18mm_W8.61mm_P2.54mm_LowProfile", "SW1", "ADDR 0x40-47", 24.5, 29.0, ref_offset=(0.0, -5.8), val_offset=(0.0, 5.8))
    set_pad_net(sw1, ["1", "2", "3"], net_3v3_iso)
    set_pad_net(sw1, "6", net_addr[2]); set_pad_net(sw1, "5", net_addr[1]); set_pad_net(sw1, "4", net_addr[0])
    board.Add(sw1)
    add_silk_text(board, "A2", 17.5, 26.46, size_mm=0.8, bold=True)
    add_silk_text(board, "A1", 17.5, 29.00, size_mm=0.8, bold=True)
    add_silk_text(board, "A0", 17.5, 31.54, size_mm=0.8, bold=True)

    r_addr = []
    for i, (pad_n, a_idx) in enumerate([("6", 2), ("5", 1), ("4", 0)]):
        swp = pad_xy(sw1, pad_n)
        ra = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RA{a_idx}", "10k", 33.5, swp[1], show_ref=False, show_val=False)
        set_pad_net(ra, "1", net_addr[a_idx]); set_pad_net(ra, "2", net_gnd_iso); board.Add(ra)
        r_addr.append((ra, a_idx, pad_n))
    add_silk_text(board, "RA0-2 10k", 33.5, 23.8, size_mm=0.8)

    # 6-Channel High-Power MOSFET Stage
    col_x = [18.5, 30.0, 41.5, 53.0, 64.5, 76.0]
    ch_parts = []
    for idx, cx in enumerate(col_x):
        ch = idx + 1
        rpd = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"R{2*ch}", "10k", cx - 3.0, 39.5, show_ref=False, show_val=False)
        set_pad_net(rpd, "1", net_pwm[idx]); set_pad_net(rpd, "2", net_gnd_iso); board.Add(rpd)

        rg = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"R{2*ch-1}", "100R", cx + 2.5, 39.5, show_ref=False, show_val=False)
        set_pad_net(rg, "1", net_pwm[idx]); set_pad_net(rg, "2", net_gate[idx]); board.Add(rg)

        q = load_fp(f"{KICAD_FP_DIR}/Package_TO_SOT_SMD.pretty", "TO-252-3_TabPin2", f"Q{ch}", "AOD4184A", cx, 47.0, angle=-90.0, ref_offset=(-4.8, 0.0), show_val=False)
        set_pad_net(q, "1", net_gate[idx]); set_pad_net(q, ["2", ""], net_out[idx]); set_pad_net(q, "3", net_gnd_iso); board.Add(q)

        d_fly = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SMA", f"D{ch}", "SS34", cx - 3.5, 55.6, angle=-90.0, show_ref=False, show_val=False)
        set_pad_net(d_fly, "1", net_24v_bus); set_pad_net(d_fly, "2", net_out[idx]); board.Add(d_fly)

        r_led = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RL{ch}", "10k", cx + 3.0, 53.0, show_ref=False, show_val=False)
        set_pad_net(r_led, "1", net_24v_bus); set_pad_net(r_led, "2", net_led[idx]); board.Add(r_led)

        led = load_fp(f"{KICAD_FP_DIR}/LED_SMD.pretty", "LED_0805_2012Metric", f"LED{ch}", "LED", cx + 3.0, 56.5, show_ref=False, show_val=False)
        set_pad_net(led, "2", net_led[idx]); set_pad_net(led, "1", net_out[idx]); board.Add(led)

        j_out_ch = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", f"J{ch+1}", f"CH{ch}", cx - 2.54, 65.5, show_ref=False, show_val=False)
        set_pad_net(j_out_ch, "1", net_24v_bus); set_pad_net(j_out_ch, "2", net_out[idx]); board.Add(j_out_ch)

        add_silk_text(board, f"CH{ch}", cx - 0.5, 54.5, size_mm=0.8, bold=True)
        add_silk_text(board, "+", cx - 2.54, 59.2, size_mm=0.85, bold=True)
        add_silk_text(board, "-", cx + 2.54, 59.2, size_mm=0.85, bold=True)
        add_silk_text(board, "+", cx - 2.54, 62.5, size_mm=1.2, bold=True, layer=pcbnew.B_SilkS)
        add_silk_text(board, "-", cx + 2.54, 62.5, size_mm=1.2, bold=True, layer=pcbnew.B_SilkS)
        ch_parts.append((rg, rpd, q, d_fly, r_led, led, j_out_ch))

    # KEAVY-BUS Pass-Through Trunk on B.Cu along y = 19.4..23.65 (100% Bus Domain!)
    ty = route_bus_trunk(board, j_in, j_out, BOARD_W, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int, y_start=19.4)

    # Tap Bus Domain -> B0505S-1W Primary (1=GND_BUS, 2=+5V_BUS) & ADuM1250ARZ Side 1 (1..4)
    dc1, dc2, dc3, dc4 = [pad_xy(u_dcdc, str(k)) for k in range(1, 5)]
    add_via(board, dc1[0] - 1.8, ty["gnd"], net_gnd_bus, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [(dc1[0] - 1.8, ty["gnd"]), (dc1[0] - 1.8, dc1[1]), dc1], 0.45, pcbnew.F_Cu, net_gnd_bus)
    add_via(board, dc2[0] + 1.9, ty["5v"], net_5v_bus, dia_mm=0.65, drill_mm=0.35)
    add_route(board, [(dc2[0] + 1.9, ty["5v"]), (dc2[0] + 1.9, dc2[1]), dc2], 0.45, pcbnew.F_Cu, net_5v_bus)

    iso_p = [pad_xy(u_iso, str(k)) for k in range(1, 9)]
    for idx_p, (snet, t_key) in enumerate([(net_3v3_bus, "3v3"), (net_sda_bus, "sda"), (net_scl_bus, "scl"), (net_gnd_bus, "gnd")]):
        ip = iso_p[idx_p]
        add_via(board, ip[0], ty[t_key], snet, dia_mm=0.60, drill_mm=0.30)
        add_track(board, ip[0], ty[t_key], ip[0], ip[1], 0.22, pcbnew.F_Cu, snet)

    # Route C_ISO1 (100nF Bus Side) & C_ISO2 (100nF Iso Side) right at U_ISO pads (zero crossings!)
    ci1_p1, ci1_p2 = pad_xy(c_iso1, "1"), pad_xy(c_iso1, "2")
    add_route(board, [ci1_p1, (iso_p[0][0], ci1_p1[1]), iso_p[0]], 0.25, pcbnew.F_Cu, net_3v3_bus)
    add_via(board, ci1_p2[0], ty["gnd"], net_gnd_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, ci1_p2[0], ci1_p2[1], ci1_p2[0], ty["gnd"], 0.25, pcbnew.F_Cu, net_gnd_bus)

    ci2_p1, ci2_p2 = pad_xy(c_iso2, "1"), pad_xy(c_iso2, "2")
    add_gnd_via_near(board, ci2_p1[0], ci2_p1[1], 0.0, 1.8, net_gnd_iso)
    add_route(board, [ci2_p2, (iso_p[7][0], ci2_p2[1]), iso_p[7]], 0.25, pcbnew.F_Cu, net_3v3_iso)

    # Isolated Power Routing: B0505S-1W (3=GND_ISO, 4=+5V_ISO) -> C_L1 -> U_LDO -> C_L2 -> +3V3_ISO
    ul_gnd, ul_out, ul_tab, ul_in = pad_xy(u_ldo, "1"), pad_xy(u_ldo, "2"), pad_xy(u_ldo, "2", "min_x"), pad_xy(u_ldo, "3")
    cl1_p1, cl1_p2 = pad_xy(c_l1, "1"), pad_xy(c_l1, "2")
    cl2_p1, cl2_p2 = pad_xy(c_l2, "1"), pad_xy(c_l2, "2")
    add_route(board, [dc4, (72.6, dc4[1]), (72.6, ul_in[1]), ul_in, (ul_in[0], cl1_p1[1]), cl1_p1], 0.45, pcbnew.F_Cu, net_5v_iso)
    add_gnd_via_near(board, cl1_p2[0], cl1_p2[1], -1.4, 0.0, net_gnd_iso)
    add_gnd_via_near(board, ul_gnd[0], ul_gnd[1], 0.0, 1.5, net_gnd_iso)
    add_track(board, ul_out[0], ul_out[1], ul_tab[0], ul_tab[1], 0.7, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [ul_tab, (cl2_p1[0], ul_tab[1]), cl2_p1], 0.4, pcbnew.F_Cu, net_3v3_iso)
    add_gnd_via_near(board, cl2_p2[0], cl2_p2[1], 0.0, 1.4, net_gnd_iso)

    # Isolated +3V3_ISO & I2C -> PCA9685 (U1), C_PWM, SW1
    u1_vdd, u1_sda, u1_scl = pad_xy(u1, "28"), pad_xy(u1, "27"), pad_xy(u1, "26")
    cpwm_p1, cpwm_p2 = pad_xy(c_pwm, "1"), pad_xy(c_pwm, "2")
    risda_p1, risda_p2 = pad_xy(r_isda, "1"), pad_xy(r_isda, "2")
    riscl_p1, riscl_p2 = pad_xy(r_iscl, "1"), pad_xy(r_iscl, "2")

    add_gnd_via_near(board, iso_p[4][0], iso_p[4][1], -1.0, 0.0, net_gnd_iso)
    add_route(board, [ul_tab, (iso_p[7][0], ul_tab[1]), iso_p[7]], 0.3, pcbnew.F_Cu, net_3v3_iso)
    # Connect +3V3_ISO from ul_tab via B.Cu (at y=25.3, below Bus Trunk & above ISO_SCL!) to R_ISCL(1)/R_ISDA(1) -> C_PWM(1) & SW1
    add_via(board, riscl_p1[0], 25.3, net_3v3_iso, dia_mm=0.60, drill_mm=0.30)
    add_track(board, risda_p1[0], risda_p1[1], riscl_p1[0], riscl_p1[1], 0.25, pcbnew.F_Cu, net_3v3_iso)
    add_track(board, riscl_p1[0], riscl_p1[1], riscl_p1[0], 25.3, 0.25, pcbnew.F_Cu, net_3v3_iso)
    add_via(board, ul_tab[0], 25.3, net_3v3_iso, dia_mm=0.60, drill_mm=0.30)
    add_track(board, ul_tab[0], ul_tab[1], ul_tab[0], 25.3, 0.3, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [(ul_tab[0], 25.3), (riscl_p1[0], 25.3)], 0.25, pcbnew.B_Cu, net_3v3_iso)
    add_route(board, [riscl_p1, (riscl_p1[0], 22.8), (cpwm_p1[0], 22.8), cpwm_p1], 0.25, pcbnew.F_Cu, net_3v3_iso, chamfer=False)
    add_route(board, [cpwm_p1, (cpwm_p1[0], u1_vdd[1]), u1_vdd], 0.25, pcbnew.F_Cu, net_3v3_iso)
    add_gnd_via_near(board, cpwm_p2[0], cpwm_p2[1], -1.6, 0.0, net_gnd_iso)

    sw_p1, sw_p3 = pad_xy(sw1, "1"), pad_xy(sw1, "3")
    add_track(board, sw_p1[0], sw_p1[1], sw_p3[0], sw_p3[1], 0.35, pcbnew.F_Cu, net_3v3_iso)
    add_route(board, [(cpwm_p1[0], 22.8), (sw_p1[0], 22.8), sw_p1], 0.3, pcbnew.F_Cu, net_3v3_iso)

    # ISO_SDA (outer right x=53.3 -> y=23.4) & ISO_SCL (B.Cu under ISO_SDA -> left x=52.4 -> y=24.0): ZERO crossings!
    add_route(board, [iso_p[6], (iso_p[6][0], 33.1), (53.3, 33.1), (53.3, 23.4), (u1_sda[0], 23.4), u1_sda], 0.20, pcbnew.F_Cu, net_sda_iso)
    add_track(board, 53.3, risda_p2[1], risda_p2[0], risda_p2[1], 0.20, pcbnew.F_Cu, net_sda_iso)
    add_route(board, [iso_p[5], (iso_p[5][0], 32.1)], 0.20, pcbnew.F_Cu, net_scl_iso)
    add_via(board, iso_p[5][0], 32.1, net_scl_iso, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [(iso_p[5][0], 32.1), (54.55, 32.1), (54.55, 25.5)], 0.20, pcbnew.B_Cu, net_scl_iso)
    add_via(board, 54.55, 25.5, net_scl_iso, dia_mm=0.60, drill_mm=0.30)
    add_track(board, 54.55, 25.5, riscl_p2[0], riscl_p2[1], 0.20, pcbnew.F_Cu, net_scl_iso)
    add_route(board, [(54.55, 25.5), (52.4, 25.5)], 0.20, pcbnew.B_Cu, net_scl_iso)
    add_via(board, 52.4, 25.5, net_scl_iso, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [(52.4, 25.5), (52.4, 24.0), (u1_scl[0], 24.0), u1_scl], 0.20, pcbnew.F_Cu, net_scl_iso)

    # PCA9685 GND pins inside chip body
    p4, p5, p14 = pad_xy(u1, "4"), pad_xy(u1, "5"), pad_xy(u1, "14")
    p23, p25 = pad_xy(u1, "23"), pad_xy(u1, "25")
    add_track(board, p4[0], p4[1], p5[0], p5[1], 0.25, pcbnew.F_Cu, net_gnd_iso)
    add_track(board, p23[0], p23[1], p25[0], p25[1], 0.25, pcbnew.F_Cu, net_gnd_iso)
    add_route(board, [p25, (p25[0], 28.5), (p4[0], 28.5), p4], 0.25, pcbnew.F_Cu, net_gnd_iso)
    add_route(board, [(p25[0], 28.5), (p14[0], 28.5), p14], 0.25, pcbnew.F_Cu, net_gnd_iso)
    add_via(board, 47.0, 28.5, net_gnd_iso, dia_mm=0.70, drill_mm=0.35)

    # DIP Switch A2,A1,A0 -> U1 Pins 3,2,1
    for i, (ra, a_idx, sw_pn) in enumerate(r_addr):
        swp = pad_xy(sw1, sw_pn)
        rap1, rap2 = pad_xy(ra, "1"), pad_xy(ra, "2")
        u1a = pad_xy(u1, str(a_idx + 1))
        add_track(board, swp[0], swp[1], rap1[0], rap1[1], 0.22, pcbnew.F_Cu, net_addr[a_idx])
        add_gnd_via_near(board, rap2[0], rap2[1], 1.5, 0.0, net_gnd_iso)
        bx = 32.0 - i * 0.72
        fy = 32.4 + i * 0.65
        add_via(board, bx, swp[1], net_addr[a_idx], dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(bx, swp[1]), (bx, fy), (u1a[0], fy)], 0.20, pcbnew.B_Cu, net_addr[a_idx])
        add_via(board, u1a[0], fy, net_addr[a_idx], dia_mm=0.60, drill_mm=0.30)
        add_track(board, u1a[0], fy, u1a[0], u1a[1], 0.20, pcbnew.F_Cu, net_addr[a_idx])

    # Power Input & Protection Routing
    f1_p1_top, f1_p1_bot = pad_xy(f1, "1", "min_y"), pad_xy(f1, "1", "max_y")
    f1_p2_top, f1_p2_bot = pad_xy(f1, "2", "min_y"), pad_xy(f1, "2", "max_y")
    add_track(board, f1_p1_top[0], f1_p1_top[1], f1_p1_bot[0], f1_p1_bot[1], 2.0, pcbnew.F_Cu, net_24v_in)
    add_track(board, f1_p2_top[0], f1_p2_top[1], f1_p2_bot[0], f1_p2_bot[1], 2.0, pcbnew.F_Cu, net_24v_fused)
    add_route(board, [j1_p1, (j1_p1[0], 3.0), (f1_p1_top[0], 3.0), f1_p1_top], 2.5, pcbnew.F_Cu, net_24v_in)

    qrev_tab, qrev_pin2, qrev_g, qrev_s = pad_xy(q_rev, "2", "max_x"), pad_xy(q_rev, "2", "first"), pad_xy(q_rev, "1"), pad_xy(q_rev, "3")
    add_track(board, qrev_pin2[0], qrev_pin2[1], qrev_tab[0], qrev_tab[1], 0.6, pcbnew.F_Cu, net_24v_fused)
    add_route(board, [f1_p2_top, (f1_p2_top[0], 3.0), (qrev_tab[0], 3.0), qrev_tab], 2.5, pcbnew.F_Cu, net_24v_fused)

    dz1_p1, dz1_p2 = pad_xy(dz1, "1"), pad_xy(dz1, "2")
    rrev_p1, rrev_p2 = pad_xy(r_rev, "1"), pad_xy(r_rev, "2")
    add_route(board, [qrev_g, (39.5, qrev_g[1]), (39.5, 14.5), (dz1_p2[0], 14.5), dz1_p2], 0.35, pcbnew.F_Cu, net_rev_gate)
    add_route(board, [dz1_p2, (dz1_p2[0], 18.0), (rrev_p1[0], 18.0), rrev_p1], 0.35, pcbnew.F_Cu, net_rev_gate)
    add_gnd_via_near(board, rrev_p2[0], rrev_p2[1], 1.5, 0.0, net_gnd_iso)

    c1_p1 = pad_xy(c1, "1")
    dtvs_p1, dtvs_p2 = pad_xy(d_tvs, "1"), pad_xy(d_tvs, "2")
    c2_p1, c2_p2 = pad_xy(c2, "1"), pad_xy(c2, "2")
    add_route(board, [qrev_s, (qrev_s[0], 13.5), (c1_p1[0], 13.5), c1_p1], 2.5, pcbnew.F_Cu, net_24v_bus)
    add_route(board, [qrev_s, (dz1_p1[0], qrev_s[1]), dz1_p1], 0.6, pcbnew.F_Cu, net_24v_bus)
    add_route(board, [c1_p1, (c1_p1[0], 15.0), (dtvs_p1[0], 15.0), dtvs_p1], 1.2, pcbnew.F_Cu, net_24v_bus)
    add_route(board, [(dtvs_p1[0], 15.0), (c2_p1[0], 15.0), c2_p1], 1.0, pcbnew.F_Cu, net_24v_bus)
    add_gnd_via_near(board, dtvs_p2[0], dtvs_p2[1], 1.8, 0.0, net_gnd_iso)
    add_gnd_via_near(board, c2_p2[0], c2_p2[1], 1.5, 0.0, net_gnd_iso)

    # PCA9685 PWM Outputs (Pins 6..11) -> 6-Channel MOSFET Drivers
    for idx, (rg, rpd, q, d_fly, r_led, led, j_out_ch) in enumerate(ch_parts):
        pwm_p = pad_xy(u1, str(6 + idx))
        rg_p1, rg_p2 = pad_xy(rg, "1"), pad_xy(rg, "2")
        rpd_p1, rpd_p2 = pad_xy(rpd, "1"), pad_xy(rpd, "2")
        q_g = pad_xy(q, "1")
        q_d_pin, q_d_tab = pad_xy(q, "2", "min_y"), pad_xy(q, "2", "max_y")
        q_s = pad_xy(q, "3")
        dfly_p2 = pad_xy(d_fly, "2")
        rled_p2 = pad_xy(r_led, "2")
        led_p1, led_p2 = pad_xy(led, "1"), pad_xy(led, "2")
        j_p2 = pad_xy(j_out_ch, "2")

        add_track(board, q_d_pin[0], q_d_pin[1], q_d_tab[0], q_d_tab[1], 0.8, pcbnew.F_Cu, net_out[idx])
        vy = [34.6, 35.3, 36.0, 36.7, 36.0, 35.1][idx]
        add_track(board, pwm_p[0], pwm_p[1], pwm_p[0], vy, 0.20, pcbnew.F_Cu, net_pwm[idx])
        add_via(board, pwm_p[0], vy, net_pwm[idx], dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(pwm_p[0], vy), (rpd_p1[0], vy)], 0.22, pcbnew.B_Cu, net_pwm[idx])
        add_via(board, rpd_p1[0], vy, net_pwm[idx], dia_mm=0.60, drill_mm=0.30)
        add_track(board, rpd_p1[0], vy, rpd_p1[0], rpd_p1[1], 0.22, pcbnew.F_Cu, net_pwm[idx])

        add_route(board, [rpd_p1, (rpd_p1[0], 37.8), (rg_p1[0], 37.8), rg_p1], 0.25, pcbnew.F_Cu, net_pwm[idx])
        add_gnd_via_near(board, rpd_p2[0], rpd_p2[1], 0.0, 1.8, net_gnd_iso)
        add_route(board, [rg_p2, (rg_p2[0], q_g[1]), q_g], 0.35, pcbnew.F_Cu, net_gate[idx])
        add_gnd_via_near(board, q_s[0], q_s[1], -1.8, 0.0, net_gnd_iso, trace_w=1.0)

        add_route(board, [q_d_tab, (q_d_tab[0], 58.5), (j_p2[0], 60.5), j_p2], 2.0, pcbnew.F_Cu, net_out[idx])
        add_route(board, [dfly_p2, (dfly_p2[0], 58.5), (q_d_tab[0], 58.5)], 1.0, pcbnew.F_Cu, net_out[idx])
        add_route(board, [led_p1, (q_d_tab[0], led_p1[1])], 0.35, pcbnew.F_Cu, net_out[idx])
        add_track(board, rled_p2[0], rled_p2[1], led_p2[0], led_p2[1], 0.3, pcbnew.F_Cu, net_led[idx])

    # High-Current +24V_BUS Feeder down x=81.6 into F.Cu +24V_BUS copper pour
    add_route(board, [c1_p1, (c1_p1[0], 13.5), (81.6, 13.5), (81.6, 51.0)], 1.8, pcbnew.F_Cu, net_24v_bus)

    # Rule #11: True 2500 Vrms Galvanic Isolation Moat — block GND_ISO pour from Bus Domain & under isolation barrier!
    add_zone_keepout(board, [(0.0, 24.0), (12.5, 24.0), (12.5, 48.0), (0.0, 48.0)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(BOARD_W - 12.5, 24.0), (BOARD_W, 24.0), (BOARD_W, 48.0), (BOARD_W - 12.5, 48.0)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(8.0, 18.2), (BOARD_W - 8.0, 18.2), (BOARD_W - 8.0, 24.6), (8.0, 24.6)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(57.5, 24.4), (66.2, 24.4), (66.2, 29.2), (57.5, 29.2)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(72.2, 24.4), (78.5, 24.4), (78.5, 28.8), (72.2, 28.8)], layers=(pcbnew.B_Cu,))

    # Bridge top & bottom GND_ISO zones on F.Cu (cleanly over FR4 dielectric at x=79.5, away from Bus pads)
    add_via(board, 79.5, 16.5, net_gnd_iso, dia_mm=0.9, drill_mm=0.45)
    add_via(board, 79.5, 31.0, net_gnd_iso, dia_mm=0.9, drill_mm=0.45)
    add_track(board, 79.5, 16.5, 79.5, 31.0, 1.2, pcbnew.F_Cu, net_gnd_iso)

    # Rule #4: Perimeter Ground Stitching Vias (Isolated Domain only, skipping Bus connectors)
    add_perimeter_gnd_stitching(board, BOARD_W, net_gnd_iso, skip_boxes=[(0.0, 15.0, 15.0, 50.0), (BOARD_W - 15.0, 15.0, BOARD_W, 50.0)])

    add_zone(board, net_gnd_iso, pcbnew.B_Cu, [(1.0, 1.0), (BOARD_W - 1.0, 1.0), (BOARD_W - 1.0, BOARD_H - 1.0), (1.0, BOARD_H - 1.0)], priority=0, clearance_mm=0.4)
    add_zone(board, net_24v_bus, pcbnew.F_Cu, [(10.5, 51.0), (85.5, 51.0), (85.5, 70.0), (10.5, 70.0)], priority=1, clearance_mm=0.3)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_path = os.path.join(PRJ_DIR, "keavy_dimmer6.kicad_pcb")
    board.Save(out_path)
    print(f"Successfully generated: {out_path}")


if __name__ == "__main__":
    build_board()
