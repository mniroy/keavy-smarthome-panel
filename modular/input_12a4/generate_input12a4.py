#!/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
"""
KEAVY-INPUT12A4 REV 2.0 (96.0 x 72.0 mm — fits SZOMK AK-P-01 115x90x40 PLC Box & UM72 DIN-Rail)
Industrial Hybrid 12-CH Opto-Isolated Digital Input + 4-CH 16-Bit 0-10V Analog Input Module:
- 12x Opto-Isolated 24V / Dry-Contact Digital Inputs (3x TLP281-4 SOP-16, 3750 Vrms isolation)
  * 6.3mA self-cleaning wetting current (3.3k 1206 resistors) + 12x series status LEDs
  * 12x 100nF hardware debounce/EMI filter caps + MCP23017 (DIP SW1 0x20-0x27, rec. 0x24-0x27)
  * Hardware Interrupt-on-Change (INTA + INTB open-drain -> KEAVY-BUS Pin 10 BUS_INT, <2ms response!)
- 4x 16-Bit 0-10V Analog Inputs (TI ADS1115IDGSR MSOP-10, I2C 0x48):
  * Precision 22k/10k 1% divider (0-10V -> 0-3.125V) + 100nF anti-aliasing RC filter
  * 3.3V Zener overvoltage/ESD clamp (BZT52C3V3) per channel (survives accidental 24V connection!)
- Predictable Designs 11 Certification Rules:
  * 45-degree chamfered routing, 24V input TVS + HF ceramic filter, True 3750V isolation moat,
    local 100nF decoupling on MCP23017 & ADS1115, Faraday-cage perimeter GND stitching vias.
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

    # 1. Nets — Bus / Logic / Analog Domain
    net_gnd_bus = add_net(board, "GND_BUS")
    net_5v_bus = add_net(board, "+5V_BUS")
    net_3v3_bus = add_net(board, "+3V3_BUS")
    net_sda_bus = add_net(board, "I2C_SDA")
    net_scl_bus = add_net(board, "I2C_SCL")
    net_bus_int = add_net(board, "BUS_INT")
    net_addr = [add_net(board, f"ADDR_A{i}") for i in range(3)]
    net_di_logic = [add_net(board, f"DI{i}_MCU") for i in range(1, 13)]
    net_ai_raw = [add_net(board, f"AI{i}_0_10V") for i in range(1, 5)]
    net_ai_adc = [add_net(board, f"ADC_AIN{i}") for i in range(4)]

    # Isolated 24V Field Domain Nets (3750 Vrms isolated via 3x TLP281-4!)
    net_24v_fld = add_net(board, "+24V_FIELD")
    net_gnd_fld = add_net(board, "GND_FIELD")
    net_di_fld = [add_net(board, f"DI{i}_FIELD") for i in range(1, 13)]
    net_di_led = [add_net(board, f"DI{i}_LED") for i in range(1, 13)]
    net_di_opto = [add_net(board, f"DI{i}_OPTO_A") for i in range(1, 13)]

    add_mounting_holes(board, BOARD_W, net_gnd_bus)

    # 2. KEAVY-BUS Left & Right Shrouded IDC Box Headers (DC3-10P)
    j_in = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_IN", "DC3-10P", 5.5, BUS_Y, ref_offset=(1.2, -7.2), val_offset=(1.2, 17.2))
    assign_keavy_bus_nets(j_in, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_in)

    j_out = load_fp(f"{KICAD_FP_DIR}/Connector_IDC.pretty", "IDC-Header_2x05_P2.54mm_Vertical", "J_BUS_OUT", "DC3-10P", BOARD_W - 7.5, BUS_Y, ref_offset=(0.5, -7.2), val_offset=(0.5, 17.2))
    assign_keavy_bus_nets(j_out, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int)
    board.Add(j_out)

    # 3. Top Edge: 24V Field Power Input + TVS + EMI Filter + MCP23017 Address DIP Switch
    j1 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal", "J1", "24V_IN", 22.0, 7.5, angle=180.0, show_ref=False, show_val=False)
    set_pad_net(j1, "1", net_24v_fld); set_pad_net(j1, "2", net_gnd_fld); board.Add(j1)
    j1_p1, j1_p2 = pad_xy(j1, "1"), pad_xy(j1, "2")
    add_silk_text(board, "+24V", j1_p1[0], 15.0, size_mm=0.85, bold=True)
    add_silk_text(board, "COM", j1_p2[0], 15.0, size_mm=0.85, bold=True)

    d_tvs = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SMB", "D_TVS", "SMBJ28A", 33.5, 9.0, ref_offset=(0.0, -3.1), val_offset=(0.0, 3.1))
    set_pad_net(d_tvs, "1", net_24v_fld); set_pad_net(d_tvs, "2", net_gnd_fld); board.Add(d_tvs)

    c1_hf = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C1_HF", "100nF 50V", 38.5, 9.0, angle=90.0, show_val=False, ref_offset=(0.0, -2.5))
    set_pad_net(c1_hf, "1", net_24v_fld); set_pad_net(c1_hf, "2", net_gnd_fld); board.Add(c1_hf)

    c1 = load_fp(f"{KICAD_FP_DIR}/Capacitor_THT.pretty", "CP_Radial_D6.3mm_P2.50mm", "C1", "100uF 35V", 43.0, 8.5, ref_offset=(1.25, -4.5), val_offset=(1.25, 4.5))
    set_pad_net(c1, "1", net_24v_fld); set_pad_net(c1, "2", net_gnd_fld); board.Add(c1)

    sw1 = load_fp(f"{KICAD_FP_DIR}/Button_Switch_SMD.pretty", "SW_DIP_SPSTx03_Slide_6.7x9.18mm_W8.61mm_P2.54mm_LowProfile", "SW1", "ADDR 0x20-27", 57.0, 10.0, ref_offset=(0.0, -6.0), val_offset=(0.0, 6.0))
    set_pad_net(sw1, ["1", "2", "3"], net_3v3_bus)
    set_pad_net(sw1, "6", net_addr[0]); set_pad_net(sw1, "5", net_addr[1]); set_pad_net(sw1, "4", net_addr[2])
    board.Add(sw1)
    add_silk_text(board, "A0", 50.0, 7.46, size_mm=0.8, bold=True)
    add_silk_text(board, "A1", 50.0, 10.00, size_mm=0.8, bold=True)
    add_silk_text(board, "A2", 50.0, 12.54, size_mm=0.8, bold=True)

    r_addr = []
    for i, pad_n in enumerate(["6", "5", "4"]):
        swp = pad_xy(sw1, pad_n)
        ra = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RA{i}", "10k", 65.5, swp[1], show_ref=False, show_val=False)
        set_pad_net(ra, "1", net_addr[i]); set_pad_net(ra, "2", net_gnd_bus); board.Add(ra)
        r_addr.append(ra)
    add_silk_text(board, "RA0-2 10k", 66.5, 4.8, size_mm=0.8)

    add_silk_text(board, "KEAVY-INPUT12A4", 79.5, 6.8, size_mm=0.8, bold=True)
    add_silk_text(board, "12DI ISO+4AI 10V", 79.5, 9.3, size_mm=0.8)
    add_silk_text(board, "0x24-27 | 0x48", 79.5, 11.8, size_mm=0.8)

    # 4. Logic ICs: MCP23017 (U7, Horizontal angle=90 at y=29.5) + ADS1115 (U_ADC, MSOP-10)
    # U7 at (37.5, 29.5) angle=90:
    #   Top row (y=24.85): Pins 28..15 left-to-right (x=29.25..45.76)
    #   Bottom row (y=34.15): Pins 1..14 left-to-right (x=29.25..45.76)
    u7 = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOIC-28W_7.5x17.9mm_P1.27mm", "U7", "MCP23017", 37.5, 29.5, angle=90.0, ref_offset=(-13.5, -1.0), val_offset=(-13.5, 1.2))
    for i in range(8):
        set_pad_net(u7, str(i + 1), net_di_logic[i])          # GPB0..7 -> DI1..DI8
    for i in range(4):
        set_pad_net(u7, str(21 + i), net_di_logic[8 + i])     # GPA0..3 -> DI9..DI12 (planar order!)
    set_pad_net(u7, ["9", "18"], net_3v3_bus)                 # VDD & ~RESET -> +3V3_BUS
    set_pad_net(u7, "10", net_gnd_bus)                        # VSS -> GND_BUS
    set_pad_net(u7, "12", net_scl_bus); set_pad_net(u7, "13", net_sda_bus)
    set_pad_net(u7, "15", net_addr[0]); set_pad_net(u7, "16", net_addr[1]); set_pad_net(u7, "17", net_addr[2])
    set_pad_net(u7, ["19", "20"], net_bus_int)                # INTB + INTA -> BUS_INT (Open-Drain!)
    board.Add(u7)

    # C_IO (angle=-90 -> Pad 1 TOP +3V3_BUS, Pad 2 BOTTOM GND_BUS)
    c_io = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_IO", "100nF", 50.2, 29.5, angle=-90.0, ref_offset=(2.8, 0.0), show_val=False)
    set_pad_net(c_io, "1", net_3v3_bus); set_pad_net(c_io, "2", net_gnd_bus); board.Add(c_io)

    # TI ADS1115IDGSR (16-bit 4-ch ADC, I2C 0x48, MSOP-10)
    u_adc = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "MSOP-10_3x3mm_P0.5mm", "U_ADC", "ADS1115", 74.5, 29.5, angle=0.0, ref_offset=(0.0, -3.6), val_offset=(0.0, 3.8))
    set_pad_net(u_adc, ["1", "3"], net_gnd_bus)   # ADDR=GND -> 0x48, GND=GND_BUS
    set_pad_net(u_adc, "4", net_ai_adc[0])        # AIN0
    set_pad_net(u_adc, "5", net_ai_adc[1])        # AIN1
    set_pad_net(u_adc, "6", net_ai_adc[2])        # AIN2
    set_pad_net(u_adc, "7", net_ai_adc[3])        # AIN3
    set_pad_net(u_adc, "8", net_3v3_bus)          # VDD
    set_pad_net(u_adc, "9", net_sda_bus)          # SDA
    set_pad_net(u_adc, "10", net_scl_bus)         # SCL
    board.Add(u_adc)

    # C_ADC (angle=-90 -> Pad 1 TOP +3V3_BUS, Pad 2 BOTTOM GND_BUS)
    c_adc = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", "C_ADC", "100nF", 80.5, 29.5, angle=-90.0, show_val=False, ref_offset=(0.0, 2.8))
    set_pad_net(c_adc, "1", net_3v3_bus); set_pad_net(c_adc, "2", net_gnd_bus); board.Add(c_adc)

    # 5. Bottom-Facing 3.81mm Screw Terminals (EXACT same footprint/pitch as KEAVY-RELAY16!)
    j2 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1-2-3.81_1x02_P3.81mm_Horizontal", "J2", "COM_GND", 13.0, 66.5, show_ref=False, show_val=False)
    set_pad_net(j2, "1", net_gnd_fld); set_pad_net(j2, "2", net_gnd_bus); board.Add(j2)

    j3 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1-8-3.81_1x08_P3.81mm_Horizontal", "J3", "DI1-DI8", 22.0, 66.5, show_ref=False, show_val=False)
    for i in range(8):
        set_pad_net(j3, str(i + 1), net_di_fld[i])
    board.Add(j3)

    j4 = load_fp(f"{KICAD_FP_DIR}/TerminalBlock_Phoenix.pretty", "TerminalBlock_Phoenix_MKDS-1-8-3.81_1x08_P3.81mm_Horizontal", "J4", "DI9-12_AI1-4", 55.5, 66.5, show_ref=False, show_val=False)
    for i in range(4):
        set_pad_net(j4, str(i + 1), net_di_fld[8 + i])
    for i in range(4):
        set_pad_net(j4, str(i + 5), net_ai_raw[i])
    board.Add(j4)

    j2_p1, j2_p2 = pad_xy(j2, "1"), pad_xy(j2, "2")
    add_silk_text(board, "C", j2_p1[0], 60.8, size_mm=0.85, bold=True)
    add_silk_text(board, "G", j2_p2[0], 60.8, size_mm=0.85, bold=True)

    di_term_pads = [pad_xy(j3, str(i + 1)) for i in range(8)] + [pad_xy(j4, str(i + 1)) for i in range(4)]
    ai_term_pads = [pad_xy(j4, str(i + 5)) for i in range(4)]

    # 6. 12-CH Opto-Isolated Digital Input Stage (3x TLP281-4 SOP-16, angle=+90 at y=46.8!)
    # At angle=+90, y=46.8:
    #   TOP row (y=43.71, Logic Transistor side): Pins 16..9 left-to-right (16C,15E, 14C,13E, 12C,11E, 10C,9E)
    #   BOTTOM row (y=49.89, Field LED side): Pins 1..8 left-to-right (1A,2K, 3A,4K, 5A,6K, 7A,8K)
    opto_xs = [27.5, 42.5, 60.5]
    optos = []
    for g, ox in enumerate(opto_xs):
        u_opt = load_fp(f"{KICAD_FP_DIR}/Package_SO.pretty", "SOP-16_4.4x10.4mm_P1.27mm", f"U_OPT{g+1}", "TLP281-4", ox, 46.8, angle=90.0, ref_offset=(0.0, 0.0), show_val=False, text_size=0.8)
        for ch_local in range(4):
            idx = g * 4 + ch_local
            a_pin = str(1 + ch_local * 2)
            k_pin = str(2 + ch_local * 2)
            c_pin = str(16 - ch_local * 2)
            e_pin = str(15 - ch_local * 2)
            set_pad_net(u_opt, a_pin, net_24v_fld)
            set_pad_net(u_opt, k_pin, net_di_opto[idx])
            set_pad_net(u_opt, c_pin, net_di_logic[idx])
            set_pad_net(u_opt, e_pin, net_gnd_bus)
        board.Add(u_opt)
        optos.append(u_opt)

    # 12x 3.3k 1206 Wetting Resistors (RD1..12), 12x Status LEDs (LED1..12), 12x 100nF Debounce Caps (CD1..12)
    # Series loop: +24V_FIELD -> U_OPT(A->K) -> RD(3.3k) -> LED(A->K) -> DIx Terminal -> Wall Switch -> COM!
    rd_parts, led_parts, cd_parts = [], [], []
    for idx, (tx, ty_pad) in enumerate(di_term_pads):
        ch = idx + 1
        rd = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_1206_3216Metric", f"RD{ch}", "3.3k", tx, 54.4, angle=-90.0, show_ref=False, show_val=False)
        set_pad_net(rd, "1", net_di_opto[idx]); set_pad_net(rd, "2", net_di_led[idx]); board.Add(rd)
        led = load_fp(f"{KICAD_FP_DIR}/LED_SMD.pretty", "LED_0805_2012Metric", f"LED{ch}", "LED", tx, 58.6, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(led, "2", net_di_led[idx]); set_pad_net(led, "1", net_di_fld[idx]); board.Add(led)
        add_silk_text(board, f"{ch}", tx, 61.1, size_mm=0.8, bold=True)
        add_silk_text(board, f"D{ch}", tx, 63.2, size_mm=0.85, bold=True, layer=pcbnew.B_SilkS)
        rd_parts.append(rd); led_parts.append(led)

        # CDx at y=40.3 (angle=+90 -> Pad 1 BOTTOM DI_MCU at y=41.25, Pad 2 TOP GND_BUS at y=39.35)
        # Clears U_OPT courtyard (top at 42.2) completely!
        u_opt = optos[idx // 4]
        c_pin = str(16 - (idx % 4) * 2)
        cp = pad_xy(u_opt, c_pin)
        cd = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", f"CD{ch}", "100nF", cp[0], 40.2, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(cd, "1", net_di_logic[idx]); set_pad_net(cd, "2", net_gnd_bus); board.Add(cd)
        cd_parts.append(cd)

    add_silk_text(board, "3.3k", 15.8, 54.4, size_mm=0.8)
    add_silk_text(board, "LED", 15.8, 58.6, size_mm=0.8)

    # 7. 4-CH 0-10V Analog Input Conditioning Stage (AI1..AI4: 22k/10k divider + 100nF RC + 3.3V Zener)
    rah_parts, ral_parts, ca_parts, da_parts = [], [], [], []
    for i, (tx, ty_pad) in enumerate(ai_term_pads):
        ch = i + 1
        rah = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RAH{ch}", "22k 1%", tx, 56.8, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(rah, "1", net_ai_raw[i]); set_pad_net(rah, "2", net_ai_adc[i]); board.Add(rah)
        ral = load_fp(f"{KICAD_FP_DIR}/Resistor_SMD.pretty", "R_0805_2012Metric", f"RAL{ch}", "10k 1%", tx, 51.8, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(ral, "1", net_ai_adc[i]); set_pad_net(ral, "2", net_gnd_bus); board.Add(ral)
        ca = load_fp(f"{KICAD_FP_DIR}/Capacitor_SMD.pretty", "C_0805_2012Metric", f"CA{ch}", "100nF", tx, 46.8, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(ca, "1", net_ai_adc[i]); set_pad_net(ca, "2", net_gnd_bus); board.Add(ca)
        da = load_fp(f"{KICAD_FP_DIR}/Diode_SMD.pretty", "D_SOD-123", f"DA{ch}", "BZT52C3V3", tx, 41.2, angle=90.0, show_ref=False, show_val=False)
        set_pad_net(da, "1", net_ai_adc[i]); set_pad_net(da, "2", net_gnd_bus); board.Add(da)

        add_silk_text(board, f"A{ch}", tx, 61.1, size_mm=0.8, bold=True)
        add_silk_text(board, f"A{ch}", tx, 63.2, size_mm=0.85, bold=True, layer=pcbnew.B_SilkS)
        rah_parts.append(rah); ral_parts.append(ral); ca_parts.append(ca); da_parts.append(da)

    add_silk_text(board, "0-10V AI", 76.5, 37.8, size_mm=0.8, bold=True)

    # 8. KEAVY-BUS Pass-Through Trunk on B.Cu along y = 17.4..21.65
    ty = route_bus_trunk(board, j_in, j_out, BOARD_W, net_5v_bus, net_gnd_bus, net_3v3_bus, net_sda_bus, net_scl_bus, net_bus_int, y_start=17.4)

    # 9. Tap KEAVY-BUS -> MCP23017 (U7), C_IO, SW1, and ADS1115 (U_ADC), C_ADC (ALL F.Cu above U7!)
    u7_vdd, u7_vss = pad_xy(u7, "9"), pad_xy(u7, "10")
    u7_scl, u7_sda = pad_xy(u7, "12"), pad_xy(u7, "13")
    u7_rst = pad_xy(u7, "18")
    u7_intb, u7_inta = pad_xy(u7, "19"), pad_xy(u7, "20")
    cio_p1, cio_p2 = pad_xy(c_io, "1"), pad_xy(c_io, "2")

    # +3V3_BUS -> C_IO(1, TOP) -> SW1(1..3), U7(18 ~RST) & U7(9 VDD)
    add_via(board, cio_p1[0], ty["3v3"], net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, cio_p1[0], ty["3v3"], cio_p1[0], cio_p1[1], 0.30, pcbnew.F_Cu, net_3v3_bus)
    add_gnd_via_near(board, cio_p2[0], cio_p2[1], 0.0, 1.5, net_gnd_bus)

    # C_IO(1) -> U7(18 ~RST) -> U7(9 VDD) cleanly via B.Cu at y=28.0 (clears C_IO Pad 2 & F.Cu SCL/SDA!)
    add_via(board, cio_p1[0], 28.0, net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, cio_p1[0], cio_p1[1], cio_p1[0], 28.0, 0.25, pcbnew.F_Cu, net_3v3_bus)
    add_route(board, [(cio_p1[0], 28.0), (u7_rst[0], 28.0)], 0.25, pcbnew.B_Cu, net_3v3_bus)
    add_via(board, u7_rst[0], 28.0, net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, u7_rst[0], 28.0, u7_rst[0], u7_rst[1], 0.25, pcbnew.F_Cu, net_3v3_bus)
    add_route(board, [(u7_rst[0], 28.0), (u7_vdd[0], 28.0), u7_vdd], 0.25, pcbnew.F_Cu, net_3v3_bus)

    # SW1 +3V3_BUS: B.Cu under F.Cu ADDR_A0..A2 (y=13.6..16.5), then F.Cu down to ty["3v3"]!
    sw_p1, sw_p3 = pad_xy(sw1, "1"), pad_xy(sw1, "3")
    add_track(board, sw_p1[0], sw_p1[1], sw_p3[0], sw_p3[1], 0.35, pcbnew.F_Cu, net_3v3_bus)
    add_route(board, [sw_p3, (50.2, sw_p3[1]), (50.2, 13.6)], 0.30, pcbnew.F_Cu, net_3v3_bus)
    add_via(board, 50.2, 13.6, net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, 50.2, 13.6, 50.2, 16.6, 0.30, pcbnew.B_Cu, net_3v3_bus)
    add_via(board, 50.2, 16.6, net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, 50.2, 16.6, 50.2, ty["3v3"], 0.30, pcbnew.F_Cu, net_3v3_bus)

    # U7 VSS(10) -> GND_BUS via inside U7 body
    add_gnd_via_near(board, u7_vss[0], u7_vss[1], 0.0, -2.0, net_gnd_bus, trace_w=0.3)

    # U7 INTA(20) & INTB(19) -> BUS_INT (Pin 10 KEAVY-BUS!)
    add_track(board, u7_inta[0], u7_inta[1], u7_intb[0], u7_intb[1], 0.22, pcbnew.F_Cu, net_bus_int)
    add_via(board, u7_inta[0], ty["int"], net_bus_int, dia_mm=0.60, drill_mm=0.30)
    add_track(board, u7_inta[0], u7_inta[1], u7_inta[0], ty["int"], 0.22, pcbnew.F_Cu, net_bus_int)

    # U7 SCL(12, left) -> outer (y=36.4, x=48.3) & SDA(13, right) -> inner (y=35.7, x=47.5): clears Pad 14!
    add_route(board, [u7_scl, (u7_scl[0], 36.4), (48.3, 36.4), (48.3, ty["scl"])], 0.22, pcbnew.F_Cu, net_scl_bus)
    add_via(board, 48.3, ty["scl"], net_scl_bus, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [u7_sda, (u7_sda[0], 35.7), (47.5, 35.7), (47.5, ty["sda"])], 0.22, pcbnew.F_Cu, net_sda_bus)
    add_via(board, 47.5, ty["sda"], net_sda_bus, dia_mm=0.60, drill_mm=0.30)

    # DIP Switch A0..A2 -> RA0..RA2 -> U7 Pins 15,16,17 (B.Cu vertical drop clears RA stubs -> F.Cu ABOVE Bus Trunk!)
    for i, (sw_pn, u7_pn) in enumerate([("6", "15"), ("5", "16"), ("4", "17")]):
        swp = pad_xy(sw1, sw_pn)
        rap1, rap2 = pad_xy(r_addr[i], "1"), pad_xy(r_addr[i], "2")
        u7a = pad_xy(u7, u7_pn)
        add_track(board, swp[0], swp[1], rap1[0], rap1[1], 0.22, pcbnew.F_Cu, net_addr[i])
        add_gnd_via_near(board, rap2[0], rap2[1], 1.5, 0.0, net_gnd_bus)
        fx = 63.2 - i * 0.70
        fy = 15.9 - i * 0.65
        add_via(board, fx, swp[1], net_addr[i], dia_mm=0.60, drill_mm=0.30)
        add_track(board, fx, swp[1], fx, fy, 0.20, pcbnew.B_Cu, net_addr[i])
        add_via(board, fx, fy, net_addr[i], dia_mm=0.60, drill_mm=0.30)
        add_route(board, [(fx, fy), (u7a[0], fy), u7a], 0.20, pcbnew.F_Cu, net_addr[i])

    # ADS1115 (U_ADC) Power, GND, I2C -> Bus Trunk
    adc_p = [pad_xy(u_adc, str(k)) for k in range(1, 11)]
    cadc_p1, cadc_p2 = pad_xy(c_adc, "1"), pad_xy(c_adc, "2")
    add_via(board, cadc_p1[0], ty["3v3"], net_3v3_bus, dia_mm=0.60, drill_mm=0.30)
    add_track(board, cadc_p1[0], ty["3v3"], cadc_p1[0], cadc_p1[1], 0.28, pcbnew.F_Cu, net_3v3_bus)
    add_route(board, [cadc_p1, (cadc_p1[0], adc_p[7][1]), adc_p[7]], 0.25, pcbnew.F_Cu, net_3v3_bus)
    add_gnd_via_near(board, cadc_p2[0], cadc_p2[1], 1.5, 0.0, net_gnd_bus)

    # ADDR(1) & GND(3) -> GND_BUS
    add_route(board, [adc_p[0], (adc_p[0][0] - 1.3, adc_p[0][1]), (adc_p[2][0] - 1.3, adc_p[2][1]), adc_p[2]], 0.22, pcbnew.F_Cu, net_gnd_bus, chamfer=False)
    add_gnd_via_near(board, adc_p[0][0] - 1.3, adc_p[0][1], -1.2, 0.0, net_gnd_bus, trace_w=0.25)

    # SDA(9) & SCL(10) -> Bus Trunk cleanly on F.Cu
    add_via(board, adc_p[9][0] + 1.2, ty["scl"], net_scl_bus, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [adc_p[9], (adc_p[9][0] + 1.2, adc_p[9][1]), (adc_p[9][0] + 1.2, ty["scl"])], 0.22, pcbnew.F_Cu, net_scl_bus)
    add_via(board, adc_p[8][0] + 2.0, ty["sda"], net_sda_bus, dia_mm=0.60, drill_mm=0.30)
    add_route(board, [adc_p[8], (adc_p[8][0] + 2.0, adc_p[8][1]), (adc_p[8][0] + 2.0, ty["sda"])], 0.22, pcbnew.F_Cu, net_sda_bus)

    # 10. Route 12-CH Optocouplers (Logic Side -> CD1..12 -> MCP23017; Field Side -> LEDs -> 3.3k -> Terminals)
    # Single clean horizontal F.Cu GND_BUS bar across all CD1..CD12 Pad 2 (top at y=39.25) with 2 end vias!
    cd_top_y = pad_xy(cd_parts[0], "2")[1]
    add_track(board, 21.0, cd_top_y, 66.0, cd_top_y, 0.35, pcbnew.F_Cu, net_gnd_bus)
    add_via(board, 21.0, cd_top_y, net_gnd_bus, dia_mm=0.70, drill_mm=0.35)
    add_via(board, 66.0, cd_top_y, net_gnd_bus, dia_mm=0.70, drill_mm=0.35)

    for g, u_opt in enumerate(optos):
        # Tie all 4 logic emitters (Pins 15, 13, 11, 9) inside top half of U_OPT body (y=45.0) to 1 clean GND via on RIGHT!
        e_pads = [pad_xy(u_opt, str(15 - k * 2)) for k in range(4)]
        for ep in e_pads:
            add_track(board, ep[0], ep[1], ep[0], 45.0, 0.25, pcbnew.F_Cu, net_gnd_bus)
        add_track(board, e_pads[0][0], 45.0, e_pads[-1][0] + 1.6, 45.0, 0.30, pcbnew.F_Cu, net_gnd_bus)
        add_via(board, e_pads[-1][0] + 1.6, 45.0, net_gnd_bus, dia_mm=0.65, drill_mm=0.35)

        for ch_local in range(4):
            idx = g * 4 + ch_local
            a_p = pad_xy(u_opt, str(1 + ch_local * 2))
            k_p = pad_xy(u_opt, str(2 + ch_local * 2))
            c_p = pad_xy(u_opt, str(16 - ch_local * 2))

            # Logic Collector -> CDx(1, BOTTOM at y=41.15)
            cd_p1 = pad_xy(cd_parts[idx], "1")
            add_track(board, c_p[0], c_p[1], cd_p1[0], cd_p1[1], 0.22, pcbnew.F_Cu, net_di_logic[idx])

            if idx < 8:
                # DI1..DI8 -> MCP23017 Bottom Pins 1..8 (planar nested B.Cu lanes: DI1..4 go right, DI5..8 go left!)
                mp = pad_xy(u7, str(idx + 1))
                if idx < 4:
                    vy = 35.1 + idx * 0.50
                else:
                    vy = 38.6 - (idx - 4) * 0.50
                vx_c = cd_p1[0]
                add_via(board, vx_c, 42.4, net_di_logic[idx], dia_mm=0.60, drill_mm=0.30)
                add_route(board, [(vx_c, 42.4), (vx_c, vy), (mp[0], vy), (mp[0], mp[1] + 0.8)], 0.20, pcbnew.B_Cu, net_di_logic[idx])
                add_via(board, mp[0], mp[1] + 0.8, net_di_logic[idx], dia_mm=0.60, drill_mm=0.30)
                add_track(board, mp[0], mp[1] + 0.8, mp[0], mp[1], 0.20, pcbnew.F_Cu, net_di_logic[idx])
            else:
                # DI9..DI12 -> MCP23017 Top Pins 21..24 (100% planar nested on B.Cu: j=0 innermost left -> lowest top!)
                j = idx - 8
                mp = pad_xy(u7, str(21 + j))
                vx_r = 52.8 + j * 0.65
                vy_bot = 38.4 - j * 0.55
                by_top = 23.9 - j * 0.50
                add_via(board, cd_p1[0], 42.4, net_di_logic[idx], dia_mm=0.60, drill_mm=0.30)
                add_route(board, [(cd_p1[0], 42.4), (cd_p1[0], vy_bot), (vx_r, vy_bot), (vx_r, by_top), (mp[0], by_top), (mp[0], mp[1] - 0.8)], 0.20, pcbnew.B_Cu, net_di_logic[idx])
                add_via(board, mp[0], mp[1] - 0.8, net_di_logic[idx], dia_mm=0.60, drill_mm=0.30)
                add_track(board, mp[0], mp[1] - 0.8, mp[0], mp[1], 0.20, pcbnew.F_Cu, net_di_logic[idx])

            # Field Side: +24V_FIELD -> U_OPT(A->K) -> RD(3.3k) -> LED -> DIx Terminal! (ZERO crossings!)
            rd_p1, rd_p2 = pad_xy(rd_parts[idx], "1"), pad_xy(rd_parts[idx], "2")
            led_p1, led_p2 = pad_xy(led_parts[idx], "1"), pad_xy(led_parts[idx], "2")
            tx, ty_pad = di_term_pads[idx]

            # U_OPT Anode -> +24V_FIELD horizontal bar on F.Cu at y=48.3 (inside bottom half of U_OPT body!)
            add_track(board, a_p[0], a_p[1], a_p[0], 48.3, 0.30, pcbnew.F_Cu, net_24v_fld)

            # U_OPT Cathode -> RD(1) via clean nested B.Cu lane (y=50.6..52.2)
            vy_op = 50.6 + ch_local * 0.50
            add_via(board, k_p[0], vy_op, net_di_opto[idx], dia_mm=0.60, drill_mm=0.30)
            add_track(board, k_p[0], k_p[1], k_p[0], vy_op, 0.22, pcbnew.F_Cu, net_di_opto[idx])
            add_route(board, [(k_p[0], vy_op), (rd_p1[0], vy_op), rd_p1], 0.25, pcbnew.B_Cu, net_di_opto[idx])
            add_via(board, rd_p1[0], rd_p1[1], net_di_opto[idx], dia_mm=0.60, drill_mm=0.30)

            # RD(2) -> LED(2, Anode) -> LED(1, Cathode) -> DIx Terminal straight down on F.Cu!
            add_track(board, rd_p2[0], rd_p2[1], led_p2[0], led_p2[1], 0.25, pcbnew.F_Cu, net_di_led[idx])
            add_track(board, led_p1[0], led_p1[1], tx, ty_pad, 0.30, pcbnew.F_Cu, net_di_fld[idx])

    # 11. Route 4-CH 0-10V Analog Input Conditioning -> ADS1115 (AIN0..AIN3)
    for i in range(4):
        tx, ty_pad = ai_term_pads[i]
        rah_p1, rah_p2 = pad_xy(rah_parts[i], "1"), pad_xy(rah_parts[i], "2")
        ral_p1, ral_p2 = pad_xy(ral_parts[i], "1"), pad_xy(ral_parts[i], "2")
        ca_p1, ca_p2 = pad_xy(ca_parts[i], "1"), pad_xy(ca_parts[i], "2")
        da_p1, da_p2 = pad_xy(da_parts[i], "1"), pad_xy(da_parts[i], "2")

        add_track(board, tx, ty_pad, rah_p1[0], rah_p1[1], 0.30, pcbnew.F_Cu, net_ai_raw[i])
        add_track(board, rah_p2[0], rah_p2[1], ral_p1[0], ral_p1[1], 0.22, pcbnew.F_Cu, net_ai_adc[i])
        add_route(board, [ral_p1, (tx - 1.3, ral_p1[1]), (tx - 1.3, ca_p1[1]), ca_p1], 0.22, pcbnew.F_Cu, net_ai_adc[i])
        add_route(board, [ca_p1, (tx - 1.3, ca_p1[1]), (tx - 1.3, da_p1[1]), da_p1], 0.22, pcbnew.F_Cu, net_ai_adc[i])
        add_gnd_via_near(board, ral_p2[0], ral_p2[1], 1.2, 0.0, net_gnd_bus, trace_w=0.25)
        add_gnd_via_near(board, ca_p2[0], ca_p2[1], 1.2, 0.0, net_gnd_bus, trace_w=0.25)
        if i < 3:
            add_gnd_via_near(board, da_p2[0], da_p2[1], 1.2, 0.0, net_gnd_bus, trace_w=0.25)
        else:
            add_gnd_via_near(board, da_p2[0], da_p2[1], 0.0, -1.4, net_gnd_bus, trace_w=0.25)

        ain_p = adc_p[3 + i]
        if i < 2:
            rx = 70.5 + i * 0.7
            add_route(board, [da_p1, (tx - 1.3, da_p1[1]), (tx - 1.3, 36.2 - i * 0.65), (rx, 36.2 - i * 0.65), (rx, ain_p[1]), ain_p], 0.20, pcbnew.F_Cu, net_ai_adc[i])
        else:
            # i=2 (AIN2, inner) -> bottom y=35.4, inner rx=77.6 -> Pin 6 (bottom)
            # i=3 (AIN3, outer) -> top y=34.6, outer rx=78.4 -> Pin 7 (top)
            j = i - 2
            rx = 77.6 + j * 0.8
            ry = 35.4 - j * 0.8
            add_route(board, [da_p1, (tx - 1.3, da_p1[1]), (tx - 1.3, ry), (rx, ry), (rx, ain_p[1]), ain_p], 0.20, pcbnew.F_Cu, net_ai_adc[i])

    # 12. 24V Field Power Feeder (+24V_FIELD & GND_FIELD — 100% Isolated from GND_BUS!)
    dtvs_p1, dtvs_p2 = pad_xy(d_tvs, "1"), pad_xy(d_tvs, "2")
    c1_p1, c1_p2 = pad_xy(c1, "1"), pad_xy(c1, "2")
    c1hf_p1, c1hf_p2 = pad_xy(c1_hf, "1"), pad_xy(c1_hf, "2")
    rd_top_y = pad_xy(rd_parts[0], "1")[1]

    add_route(board, [j1_p1, (j1_p1[0], 12.8), (dtvs_p1[0], 12.8), dtvs_p1], 1.2, pcbnew.F_Cu, net_24v_fld)
    add_route(board, [(dtvs_p1[0], 12.8), (c1_p1[0], 12.8), c1_p1], 1.2, pcbnew.F_Cu, net_24v_fld)
    add_track(board, c1hf_p1[0], c1hf_p1[1], c1hf_p1[0], 12.8, 0.5, pcbnew.F_Cu, net_24v_fld)

    add_route(board, [j1_p2, (j1_p2[0], 4.0), (dtvs_p2[0], 4.0), dtvs_p2], 1.0, pcbnew.F_Cu, net_gnd_fld)
    add_route(board, [(dtvs_p2[0], 4.0), (c1hf_p2[0], 4.0), c1hf_p2], 0.5, pcbnew.F_Cu, net_gnd_fld)
    add_route(board, [(c1hf_p2[0], 4.0), (c1_p2[0], 4.0), c1_p2], 0.8, pcbnew.F_Cu, net_gnd_fld)
    add_route(board, [j1_p2, (14.2, j1_p2[1]), (14.2, j2_p1[1]), j2_p1], 1.0, pcbnew.F_Cu, net_gnd_fld)

    # +24V_FIELD horizontal rail on F.Cu at y=48.3 feeding all 12 U_OPT Anodes (ZERO crossings!)
    add_route(board, [(j1_p1[0], 12.8), (16.5, 12.8), (16.5, 48.3), (pad_xy(optos[-1], "7")[0], 48.3)], 0.9, pcbnew.F_Cu, net_24v_fld)

    # 13. Rule #11: True 3750 Vrms Galvanic Isolation Moat — block GND_BUS pour from ALL Field 24V areas!
    add_zone_keepout(board, [(12.5, 0.0), (47.0, 0.0), (47.0, 15.2), (12.5, 15.2)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(12.5, 14.5), (18.5, 14.5), (18.5, BOARD_H), (12.5, BOARD_H)], layers=(pcbnew.B_Cu,))
    add_zone_keepout(board, [(12.5, 46.5), (68.2, 46.5), (68.2, BOARD_H), (12.5, BOARD_H)], layers=(pcbnew.B_Cu,))

    # Connect J2 Pin 2 (AGND = GND_BUS) via clean B.Cu bridge from Analog GND zone
    add_route(board, [j2_p2, (j2_p2[0], 69.5), (70.0, 69.5)], 0.8, pcbnew.B_Cu, net_gnd_bus)

    # Rule #4: Perimeter Ground Stitching Vias (Logic/Analog Domain only, skipping Field 24V zones!)
    add_perimeter_gnd_stitching(
        board, BOARD_W, net_gnd_bus,
        skip_boxes=[
            (11.0, 0.0, 48.0, 16.0),
            (11.0, 44.5, 69.0, BOARD_H),
            (0.0, 23.0, 14.0, 49.0),
            (BOARD_W - 14.0, 23.0, BOARD_W, 49.0),
        ],
    )

    add_zone(board, net_gnd_bus, pcbnew.B_Cu, [(1.0, 1.0), (BOARD_W - 1.0, 1.0), (BOARD_W - 1.0, BOARD_H - 1.0), (1.0, BOARD_H - 1.0)], priority=0, clearance_mm=0.4)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_path = os.path.join(PRJ_DIR, "keavy_input12a4.kicad_pcb")
    board.Save(out_path)
    print(f"Successfully generated: {out_path}")


if __name__ == "__main__":
    build_board()
