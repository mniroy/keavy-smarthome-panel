"""Shared KiCad 10 PCB generation helpers for KEAVY Modular DIN-Rail System (UM72 72mm)."""

import math
import pcbnew
from PIL import Image

KICAD_FP_DIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
BOARD_H = 72.0      # Standard UM72 DIN-rail carrier width
CORNER_R = 3.0
BUS_Y = 31.0        # Standardized KEAVY-BUS 2x5 horizontal connector Y origin (pads y=31.0..41.16)


def mm(val):
    return pcbnew.FromMM(val)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def pad_xy(fp, pad_name, pick="first"):
    matches = []
    for p in fp.Pads():
        if p.GetName() == str(pad_name):
            pos = p.GetPosition()
            matches.append((pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))
    if not matches:
        raise KeyError(f"Pad {pad_name} not found in {fp.GetReference()}")
    if pick == "max_y":
        return max(matches, key=lambda c: c[1])
    if pick == "min_y":
        return min(matches, key=lambda c: c[1])
    if pick == "max_x":
        return max(matches, key=lambda c: c[0])
    if pick == "min_x":
        return min(matches, key=lambda c: c[0])
    return matches[0]


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def load_fp(lib_dir, fp_name, ref, val, x, y, angle=0.0, val_offset=(0, 2.8), ref_offset=(0, -2.8), show_val=True, show_ref=True, text_size=0.8, text_thick=0.13, ref_angle=0.0, val_angle=0.0):
    fp = pcbnew.FootprintLoad(lib_dir, fp_name)
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(pt(x, y))
    if angle != 0.0:
        fp.SetOrientationDegrees(angle)

    ref_txt = fp.Reference()
    ref_txt.SetVisible(show_ref)
    ref_txt.SetLayer(pcbnew.F_SilkS)
    ref_txt.SetTextSize(pcbnew.VECTOR2I(mm(text_size), mm(text_size)))
    ref_txt.SetTextThickness(mm(text_thick))
    ref_txt.SetTextAngleDegrees(ref_angle)
    ref_txt.SetPosition(pt(x + ref_offset[0], y + ref_offset[1]))

    val_txt = fp.Value()
    val_txt.SetVisible(show_val)
    val_txt.SetLayer(pcbnew.F_SilkS)
    val_txt.SetTextSize(pcbnew.VECTOR2I(mm(text_size), mm(text_size)))
    val_txt.SetTextThickness(mm(text_thick))
    val_txt.SetTextAngleDegrees(val_angle)
    val_txt.SetPosition(pt(x + val_offset[0], y + val_offset[1]))
    return fp


def set_pad_net(fp, pad_names, net):
    if isinstance(pad_names, str):
        pad_names = [pad_names]
    for pad in fp.Pads():
        if pad.GetName() in pad_names:
            pad.SetNet(net)


def add_track(board, x1, y1, x2, y2, width_mm, layer, net):
    if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
        return None
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pt(x1, y1))
    t.SetEnd(pt(x2, y2))
    t.SetWidth(mm(width_mm))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)
    return t


def chamfer_points(pts, max_r=0.45):
    """
    Replaces 90-degree orthogonal corners with 45-degree chamfers (bevels).
    Follows high-reliability PCB best practices:
    - Eliminates acid traps at sharp corners during copper etching.
    - Reduces impedance discontinuity and high-frequency EMI reflection.
    """
    if len(pts) <= 2:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p_prev = out[-1]
        p_curr = pts[i]
        p_next = pts[i + 1]

        v1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
        v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])
        l1 = math.hypot(v1[0], v1[1])
        l2 = math.hypot(v2[0], v2[1])
        if l1 < 1e-4 or l2 < 1e-4:
            continue

        dot = v1[0] * v2[0] + v1[1] * v2[1]
        cos_theta = dot / (l1 * l2)
        # Orthogonal 90-degree turns have cos_theta ~ 0
        if abs(cos_theta) < 0.25:
            r = min(max_r, l1 * 0.35, l2 * 0.35)
            if r >= 0.08:
                p1a = (round(p_curr[0] - (v1[0] / l1) * r, 4), round(p_curr[1] - (v1[1] / l1) * r, 4))
                p1b = (round(p_curr[0] + (v2[0] / l2) * r, 4), round(p_curr[1] + (v2[1] / l2) * r, 4))
                out.append(p1a)
                out.append(p1b)
                continue
        out.append(p_curr)
    out.append(pts[-1])
    return out


def add_route(board, pts, width_mm, layer, net, chamfer=True):
    if chamfer and len(pts) > 2:
        pts = chamfer_points(pts)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        add_track(board, x1, y1, x2, y2, width_mm, layer, net)


def add_via(board, x, y, net, dia_mm=0.8, drill_mm=0.4):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y))
    v.SetWidth(pcbnew.F_Cu, mm(dia_mm))
    v.SetDrill(mm(drill_mm))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetNet(net)
    board.Add(v)
    return v


def add_gnd_via_near(board, x, y, dx, dy, net_gnd, trace_w=0.5):
    vx, vy = x + dx, y + dy
    add_track(board, x, y, vx, vy, trace_w, pcbnew.F_Cu, net_gnd)
    add_via(board, vx, vy, net_gnd, dia_mm=0.85, drill_mm=0.4)


def add_silk_text(board, text, x, y, size_mm=1.0, thickness_mm=0.16, angle=0.0, bold=False, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pt(x, y))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size_mm), mm(size_mm)))
    t.SetTextThickness(mm(thickness_mm))
    t.SetLayer(layer)
    t.SetBold(bold)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    if angle != 0.0:
        t.SetTextAngleDegrees(angle)
    board.Add(t)
    return t


def add_board_outline(board, board_w, board_h=BOARD_H, corner_r=CORNER_R):
    w, h, r = board_w, board_h, corner_r
    edges = [
        ((r, 0), (w - r, 0)),
        ((w, r), (w, h - r)),
        ((w - r, h), (r, h)),
        ((0, h - r), (0, r)),
    ]
    for (x1, y1), (x2, y2) in edges:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.15))
        seg.SetStart(pt(x1, y1))
        seg.SetEnd(pt(x2, y2))
        board.Add(seg)

    d = r * (1.0 - math.sqrt(0.5))
    corners = [
        ((0, r), (d, d), (r, 0)),
        ((w - r, 0), (w - d, d), (w, r)),
        ((w, h - r), (w - d, h - d), (w - r, h)),
        ((r, h), (d, h - d), (0, h - r)),
    ]
    for s, m, e in corners:
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.15))
        arc.SetArcGeometry(pt(*s), pt(*m), pt(*e))
        board.Add(arc)


def add_mounting_holes(board, board_w, net_gnd, board_h=BOARD_H):
    for idx, (mx, my) in enumerate([(5, 5), (board_w - 5, 5), (5, board_h - 5), (board_w - 5, board_h - 5)], 1):
        mh = load_fp(
            f"{KICAD_FP_DIR}/MountingHole.pretty",
            "MountingHole_3.2mm_M3_Pad_Via",
            f"H{idx}", "M3", mx, my, show_val=False
        )
        mh.Reference().SetVisible(False)
        set_pad_net(mh, "1", net_gnd)
        board.Add(mh)


def add_zone(board, net, layer, points_mm, priority=0, clearance_mm=0.35):
    zone = pcbnew.ZONE(board)
    zone.SetNet(net)
    zone.SetLayer(layer)
    zone.SetAssignedPriority(priority)
    zone.SetLocalClearance(mm(clearance_mm))
    zone.SetMinThickness(mm(0.25))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetThermalReliefGap(mm(0.25))
    zone.SetThermalReliefSpokeWidth(mm(0.35))

    outline = zone.Outline()
    outline.NewOutline()
    for x, y in points_mm:
        outline.Append(mm(x), mm(y))
    board.Add(zone)
    return zone


def add_keepout_zone(board, points_mm):
    zone = pcbnew.ZONE(board)
    zone.SetIsRuleArea(True)
    zone.SetDoNotAllowTracks(True)
    zone.SetDoNotAllowVias(True)
    zone.SetDoNotAllowZoneFills(True)
    lset = pcbnew.LSET()
    lset.AddLayer(pcbnew.F_Cu)
    lset.AddLayer(pcbnew.B_Cu)
    zone.SetLayerSet(lset)

    outline = zone.Outline()
    outline.NewOutline()
    for x, y in points_mm:
        outline.Append(mm(x), mm(y))
    board.Add(zone)
    return zone


def add_logo_from_png(board, png_path, x0, y0, target_width_mm=18.0):
    im = Image.open(png_path).convert("RGBA")
    orig_w, orig_h = im.size
    new_w = 220
    new_h = max(1, int(round(orig_h * (new_w / orig_w))))
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    pixel_size = target_width_mm / new_w
    pixels = im.load()

    for row in range(new_h):
        in_run = False
        run_start = 0
        for col in range(new_w + 1):
            is_on = False
            if col < new_w:
                r, g, b, a = pixels[col, row]
                if a > 128 and (r + g + b) / 3 > 128:
                    is_on = True
            if is_on and not in_run:
                in_run = True
                run_start = col
            elif not is_on and in_run:
                in_run = False
                rx1 = x0 + run_start * pixel_size
                rx2 = x0 + col * pixel_size
                ry1 = y0 + row * pixel_size
                ry2 = y0 + (row + 1.05) * pixel_size
                rect = pcbnew.PCB_SHAPE(board)
                rect.SetShape(pcbnew.SHAPE_T_RECT)
                rect.SetLayer(pcbnew.F_SilkS)
                rect.SetFilled(True)
                rect.SetWidth(mm(0.01))
                rect.SetStart(pt(rx1, ry1))
                rect.SetEnd(pt(rx2, ry2))
                board.Add(rect)


def assign_keavy_bus_nets(fp, net_5v, net_gnd, net_3v3, net_sda, net_scl, net_int):
    """
    Assign standardized REV 2.0 10-pin KEAVY-BUS nets (DC3-10P, EMI-shielded):
      Pin 1,2 = +5V_BUS | Pin 3,4,6,8 = GND_BUS (Pin 8 shields SDA from SCL!)
      Pin 5   = +3V3_BUS | Pin 7 = I2C_SDA | Pin 9 = I2C_SCL | Pin 10 = BUS_INT
    """
    set_pad_net(fp, ["1", "2"], net_5v)
    set_pad_net(fp, ["3", "4", "6", "8"], net_gnd)
    set_pad_net(fp, "5", net_3v3)
    set_pad_net(fp, "7", net_sda)
    set_pad_net(fp, "9", net_scl)
    set_pad_net(fp, "10", net_int)


def route_bus_trunk(board, j_in, j_out, board_w, net_5v, net_gnd, net_3v3, net_sda, net_scl, net_int, y_start=17.4):
    """
    Clean zero-crossing B.Cu pass-through trunk between left & right DC3-10P headers.
    Includes explicit GND_BUS trunk so GND_BUS stays 100% galvanically isolated from GND_ISO!
    Returns dict of trunk Y coordinates for tapping into U_DCDC (B0505S-1W) and U_ISO (ADuM1250ARZ).
    """
    for jh in (j_in, j_out):
        p1, p2 = pad_xy(jh, "1"), pad_xy(jh, "2")
        add_track(board, p1[0], p1[1], p2[0], p2[1], 0.6, pcbnew.B_Cu, net_5v)
        p3, p4, p6, p8 = pad_xy(jh, "3"), pad_xy(jh, "4"), pad_xy(jh, "6"), pad_xy(jh, "8")
        add_route(board, [p3, p4, p6, p8], 0.5, pcbnew.F_Cu, net_gnd)

    # Specs: (pad_l, pad_r, dy_l, right_on_fcu, xr_slot, net, width, key)
    specs = [
        ("2",  "1",   0.0,   False, 0, net_5v,  0.50, "5v"),
        ("4",  "3",   0.0,   False, 1, net_gnd, 0.50, "gnd"),
        ("5",  "5",  -1.27,  False, 2, net_3v3, 0.30, "3v3"),
        ("7",  "7",  -1.27,  False, 3, net_sda, 0.22, "sda"),
        ("9",  "9",  -1.27,  False, 4, net_scl, 0.22, "scl"),
        ("10", "10",  0.0,   True,  5, net_int, 0.22, "int"),
    ]
    trunk_y = {}
    for idx, (pl_n, pr_n, dyl, r_fcu, xr_slot, snet, tw, key) in enumerate(specs):
        ty = y_start + idx * 0.85
        trunk_y[key] = ty
        pl, pr = pad_xy(j_in, pl_n), pad_xy(j_out, pr_n)
        xl = 9.8 + idx * 0.72
        xr = board_w - 9.3 - xr_slot * 0.72
        pts = [pl]
        if abs(dyl) > 1e-3:
            pts.append((pl[0], pl[1] + dyl))
        pts.extend([(xl, pl[1] + dyl), (xl, ty), (xr, ty)])
        if r_fcu:
            add_route(board, pts, tw, pcbnew.B_Cu, snet)
            add_via(board, xr, ty, snet, dia_mm=0.60, drill_mm=0.30)
            add_route(board, [(xr, ty), (xr, pr[1] + 1.27), (pr[0], pr[1] + 1.27), pr], tw, pcbnew.F_Cu, snet)
        else:
            pts.extend([(xr, pr[1]), pr])
            add_route(board, pts, tw, pcbnew.B_Cu, snet)
    return trunk_y
