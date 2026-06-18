#!/usr/bin/env python3

from os import mkdir, listdir, path
from pathlib import Path
import re
import subprocess
import json
from collections import OrderedDict

# Pre-compile regex for performance
_HEX_RE = re.compile(r"^[0-9a-fA-F]{16}$")
_HEADER_RE = re.compile(r"(\[.+\]|\{.+\})")
_CODE_RE = re.compile(r"[0-9a-fA-F]{8}")


class ProcessCheats:
    def __init__(self, in_path, out_path):
        self.out_path = Path(out_path)
        self.in_path = Path(in_path)
        self.parseCheats()

    def isHexAnd16Char(self, file_name):
        # Optimization: Use pre-compiled regex instead of manual character checking
        return bool(_HEX_RE.match(file_name))

    def getCheatsPath(self, tid):
        for folder in tid.iterdir():
            if folder.name.lower() == "cheats":
                return folder
        return None

    def getAttribution(self, tid):
        attribution = OrderedDict()
        for f in tid.iterdir():
            if f.suffix.lower() == ".txt":
                with open(f, "r") as attribution_file:
                    attribution[f.name] = attribution_file.read()
        return attribution

    def constructBidDict(self, sheet_path):
        """
        Parses a cheat sheet into a dictionary.
        Optimization: Single-pass iteration over lines instead of multiple regex searches.
        """
        out = OrderedDict()
        with open(sheet_path, 'r', encoding="utf-8", errors="ignore") as cheatSheet:
            lines = cheatSheet.readlines()

        current_title = None
        current_block = []

        for line in lines:
            header_match = _HEADER_RE.search(line)
            if header_match:
                # If we were already tracking a cheat, flush it if it contains valid code
                if current_title and len(current_block) > 1:
                    code = "".join(current_block)
                    if _CODE_RE.search(code):
                        out[current_title] = code.strip("\n ") + "\n\n"

                current_title = line.strip()
                current_block = [line]
            elif current_title:
                current_block.append(line)

        # Flush the last cheat
        if current_title and len(current_block) > 1:
            code = "".join(current_block)
            if _CODE_RE.search(code):
                out[current_title] = code.strip("\n ") + "\n\n"

        return out

    def update_dict(self, new, old):
        for key, value in new.items():
            if key in old:
                old[key] |= value
            else:
                old[key] = value
        return old

    def createJson(self, tid):
        out = OrderedDict()
        cheats_dir = self.getCheatsPath(tid)
        if cheats_dir:
            try:
                for sheet in cheats_dir.iterdir():
                    if self.isHexAnd16Char(sheet.stem):
                        out[sheet.stem.upper()] = self.constructBidDict(sheet)
            except FileNotFoundError:
                print(f"error: FileNotFoundError {folder_path}")
            attribution = self.getAttribution(tid)
            if attribution:
                out = self.update_dict(out, {"attribution": attribution})

            cheats_file = self.out_path.joinpath(f"{tid.name.upper()}.json")
            try:
                with open(cheats_file, 'r') as json_file:
                    out = self.update_dict(out, json.load(json_file))
            except FileNotFoundError:
                pass

            out = OrderedDict(sorted(out.items()))

            with open(cheats_file, 'w') as json_file:
                json.dump(out, json_file, indent=4)

    def parseCheats(self):
        subprocess.call(['bash', '-c', f"chmod -R +rw {self.in_path}"])
        if not(self.out_path.exists()):
            self.out_path.mkdir()
        for tid in self.in_path.iterdir():
            if self.isHexAnd16Char(tid.name):
                self.createJson(tid)
