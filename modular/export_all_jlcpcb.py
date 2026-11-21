#!/usr/bin/env python3
"""Export JLCPCB Gerber ZIP + BOM + CPL for all 3 KEAVY Modular DIN-Rail PCBs."""

import csv
import os
import shutil
import subprocess
import sys
import zipfile

MODULAR_DIR = os.path.dirname(os.path.abspath(__file__))
KICAD_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

LCSC_MAP = {
    "AOD4184A": "C428236",
    "AOD403": "C28969",
    "MCP23017": "C47023",
    "PCA9685PW": "C444771",
    "ULN2803G": "C7512",
    "ADuM1250ARZ": "C53520",
    "B0505S-1W": "C18619",
    "USBLC6-2SC6": "C7519",
    "XL1509-5.0": "C61063",
    "W5500": "C32843",
    "AMS1117-3.3": "C6186",
    "SS34": "C2400",
    "BZT52C12": "C80671",
    "SMBJ28A": "C98226",
    "33uH 3A": "C168344",
    "25MHz": "C112312",
    "47R": "C17713",
    "100R": "C17414",
    "1k": "C17513",
    "2.2k": "C17520",
    "4.7k": "C17673",
    "10k": "C17415",
    "100k": "C17407",
    "12.4k": "C25744",
    "500mA PTC": "C369156",
    "100nF": "C49678",
    "10uF": "C15850",
    "10uF 50V": "C13585",
    "100uF 35V": "C331289",
    "220uF 16V": "C331301",
    "470uF 35V": "C331317",
    "LED": "C2297",
    "LED GRN": "C2297",
    "3A FUSE": "C236378",
    "15A FUSE": "C236378",
    "24V_IN": "C8465",
    "24V_OUT": "C395891",
    "CH1-CH8": "C395897",
    "CH9-CH16": "C395897",
    "CH1": "C8465", "CH2": "C8465", "CH3": "C8465",
    "CH4": "C8465", "CH5": "C8465", "CH6": "C8465",
    "HR911105A LAN": "C12074",
    "ESP32-DevKit-30P": "C225447",
    "DC3-10P": "C49661",
    "KEAVY-BUS": "C49661",
    "BUS_OUT": "C49661",
    "BUS_IN": "C49661",
    "ADDR 0x20-27": "C410099",
    "ADDR 0x40-47": "C410099",
}


def export_board(subdir, name):
    sys.path.append("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
    import pcbnew

    pcb_file = os.path.join(MODULAR_DIR, subdir, f"{name}.kicad_pcb")
    out_dir = os.path.join(MODULAR_DIR, subdir, "manufacturing", "jlcpcb")
    tmp_dir = os.path.join(out_dir, "gerbers_tmp")
    os.makedirs(out_dir, exist_ok=True)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    subprocess.check_call([KICAD_CLI, "pcb", "export", "gerbers", "--output", tmp_dir, "--subtract-soldermask", "--check-zones", pcb_file])
    subprocess.check_call([KICAD_CLI, "pcb", "export", "drill", "--output", tmp_dir, "--format", "excellon", "--excellon-units", "mm", pcb_file])

    zip_path = os.path.join(out_dir, f"GERBER-{name}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(tmp_dir)):
            fp = os.path.join(tmp_dir, fn)
            if os.path.isfile(fp):
                zf.write(fp, arcname=fn)
    shutil.rmtree(tmp_dir)

    board = pcbnew.LoadBoard(pcb_file)
    bom_groups, cpl_rows = {}, []
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        ref, val, pkg = fp.GetReference(), fp.GetValue(), str(fp.GetFPID().GetLibItemName())
        if ref.startswith("H") and "MountingHole" in pkg:
            continue
        pos = fp.GetPosition()
        lcsc = LCSC_MAP.get(val, LCSC_MAP.get(ref, ""))
        bom_groups.setdefault((val, pkg, lcsc), []).append(ref)
        cpl_rows.append({
            "Designator": ref, "Val": val, "Package": pkg,
            "Mid X": f"{pcbnew.ToMM(pos.x):.2f}", "Mid Y": f"{-pcbnew.ToMM(pos.y):.2f}",
            "Rotation": f"{fp.GetOrientation().AsDegrees() % 360.0:.1f}",
            "Layer": "Top" if fp.GetLayer() == pcbnew.F_Cu else "Bottom",
        })

    with open(os.path.join(out_dir, f"BOM-{name}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (val, pkg, lcsc), refs in bom_groups.items():
            w.writerow([val, ",".join(refs), pkg, lcsc])

    with open(os.path.join(out_dir, f"CPL-{name}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
        w.writeheader()
        w.writerows(cpl_rows)

    print(f"Exported JLCPCB package for {name} -> {out_dir}")


if __name__ == "__main__":
    for sub, nm in [("brain", "keavy_brain"), ("relay_16ch", "keavy_relay16"), ("dimmer_6ch", "keavy_dimmer6")]:
        export_board(sub, nm)
