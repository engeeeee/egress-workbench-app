#!/usr/bin/env python3
"""Statically inventory plain Nuitka 4.3.3 constant blobs; never load binaries.

Format references (not vendored or executed):
https://github.com/Nuitka/Nuitka/blob/4.3.3/nuitka/build/static_src/HelpersConstantsBlob.c
https://github.com/Nuitka/Nuitka/blob/4.3.3/nuitka/build/include/nuitka/constants_blob_spec.h

This recovers constants and code metadata, not executable Python function bodies.
Only the uncompressed, little-endian format observed in this release is supported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct


class DecodeError(ValueError):
    pass


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.functions: list[dict] = []
        self.strings: list[str] = []

    def take(self, count: int) -> bytes:
        if count < 0 or self.pos + count > len(self.data):
            raise DecodeError(f"Truncated value at {self.pos:#x}")
        value = self.data[self.pos:self.pos + count]
        self.pos += count
        return value

    def uint(self) -> int:
        value = 0
        for shift in range(0, 70, 7):
            byte = self.take(1)[0]
            value |= (byte & 127) << shift
            if byte < 128:
                return value
        raise DecodeError("Oversized variable-length integer")

    def cstring(self) -> bytes:
        end = self.data.find(b"\0", self.pos)
        if end < 0:
            raise DecodeError("Unterminated string")
        return self.take(end - self.pos + 1)[:-1]

    def sequence(self, count: int, depth: int) -> list:
        if count > len(self.data):
            raise DecodeError("Unreasonable collection length")
        result = []
        for _ in range(count):
            if self.data[self.pos:self.pos + 1] == b"p":
                self.pos += 1
                if not result:
                    raise DecodeError("Repeat without previous sibling")
                result.append(result[-1])
            else:
                result.append(self.value(depth + 1))
        return result

    def code(self, tag: str, depth: int) -> dict:
        flags = self.uint()
        if tag == "K":
            name, line, variables, argc = "<module>", 1, [], 0
        else:
            name = "<genexpr>" if tag == "Y" else self.value(depth + 1)
            line = self.uint() + 1
            variables = self.value(depth + 1)
            argc = 0 if tag == "W" else 1 if tag == "Y" else self.uint()
        qualified = self.value(depth + 1) if flags & 1 else name
        free_vars = self.value(depth + 1) if flags & 2 else []
        kw_only = self.uint() + 1 if flags & 4 else 0
        pos_only = self.uint() + 1 if flags & 8 else 0
        record = {
            "kind": {"K": "module", "W": "class", "Y": "generator", "C": "function"}[tag],
            "name": name, "qualname": qualified, "line": line,
            "variables": variables, "arg_count": argc, "kw_only": kw_only,
            "pos_only": pos_only, "varargs": bool(flags & 256),
            "varkwargs": bool(flags & 512), "free_vars": free_vars, "flags": flags,
        }
        self.functions.append(record)
        return record

    def value(self, depth: int = 0):
        if depth > 100:
            raise DecodeError("Excessive nesting")
        start = self.pos
        tag = chr(self.take(1)[0])
        if tag in "nFt":
            return {"n": None, "F": False, "t": True}[tag]
        if tag in "auvcwdsbBXOE":
            if tag in "aucOE":
                raw = self.cstring()
            elif tag in "wd":
                raw = self.take(1)
            elif tag == "s":
                raw = b""
            else:
                raw = self.take(self.uint())
            if tag in "cdbBX":
                return {"kind": "bytes" if tag != "X" else "blob", "hex": raw.hex()}
            text = raw.decode("utf-8", "surrogatepass")
            if tag in "OE":
                return {"kind": "builtin" if tag == "O" else "exception", "name": text}
            self.strings.append(text)
            return text
        if tag in "lqiI":
            value = self.uint()
            return -value if tag in "qI" else value
        if tag in "gG":
            value = 0
            for _ in range(self.uint()):
                value = (value << 31) + self.uint()
            return -value if tag == "G" else value
        if tag == "f":
            return struct.unpack("<d", self.take(8))[0]
        if tag == "Z":
            return {"kind": "special_float", "index": self.take(1)[0]}
        if tag in "jJ":
            parts = list(struct.unpack("<dd", self.take(16))) if tag == "j" else self.sequence(2, depth)
            return {"kind": "complex", "parts": parts}
        if tag in "TLSP":
            values = self.sequence(self.uint(), depth)
            if tag in "TL":
                return values
            return {"kind": "set" if tag == "S" else "frozenset", "values": values}
        if tag in "De":
            count = self.uint()
            keys, values = self.sequence(count, depth), self.sequence(count, depth)
            return {"kind": "dict" if tag == "D" else "frozendict", "items": list(zip(keys, values))}
        if tag in ":;":
            return {"kind": "slice" if tag == ":" else "range", "values": self.sequence(3, depth)}
        if tag in "MQ":
            return {"kind": "anonymous" if tag == "M" else "special", "index": self.take(1)[0]}
        if tag in "AH":
            return {"kind": "generic_alias" if tag == "A" else "union", "values": self.sequence(2 if tag == "A" else 1, depth)}
        if tag in "CKWY":
            return self.code(tag, depth)
        raise DecodeError(f"Unsupported tag {tag!r} at {start:#x}")

    def decode(self) -> list:
        count = struct.unpack("<H", self.take(2))[0]
        result = self.sequence(count, 0)
        if self.take(1) != b"." or self.pos != len(self.data):
            raise DecodeError(f"Bad constant block boundary at {self.pos:#x}")
        return result


def blocks(data: bytes, start: int, terminal: str | None = None):
    position = start
    seen = set()
    while position < len(data):
        end = data.find(b"\0", position, position + 512)
        if end < 0:
            raise DecodeError("Missing module name")
        name = data[position:end].decode("ascii")
        if name == "sentinel":
            return
        if name in seen or not re.fullmatch(r"[.a-zA-Z_0-9]*", name):
            raise DecodeError(f"Invalid module name {name!r}")
        seen.add(name)
        if end + 5 > len(data):
            raise DecodeError("Truncated block size")
        size = struct.unpack_from("<I", data, end + 1)[0]
        position = end + 5
        if size < 3 or position + size > len(data):
            raise DecodeError(f"Invalid size for {name!r}")
        yield name, position, data[position:position + size]
        if name == terminal:
            return
        position += size
    raise DecodeError("Missing blob sentinel")


def inspect(path: Path, output: Path) -> dict:
    data = path.read_bytes()
    candidates = [m.start() for m in re.finditer(rb"\.bytecode\0", data)]
    failures = []
    # The single-module Linux extensions omit the host package's sentinel.
    terminal = path.name.partition(".cpython-")[0] if data.startswith(b"\x7fELF") else None
    for start in candidates:
        try:
            records = list(blocks(data, start, terminal))
            if not records or records[0][0] != ".bytecode":
                continue
            parsed = []
            for name, offset, raw in records:
                reader = Reader(raw)
                values = reader.decode()
                parsed.append({
                    "module": name, "offset": offset, "bytes": len(raw),
                    "constant_count": len(values), "constants": values,
                    "functions": reader.functions,
                    "strings": list(dict.fromkeys(reader.strings)),
                })
        except (DecodeError, UnicodeError, struct.error, RecursionError) as error:
            failures.append(f"{start:#x}: {error}")
            continue
        summary = {
            "schema": 1, "input": str(path.resolve()),
            "sha256": hashlib.sha256(data).hexdigest(),
            "blob_offset": start, "module_count": len(parsed),
            "code_record_count": sum(len(r["functions"]) for r in parsed),
            "function_count": sum(f["kind"] == "function" for r in parsed for f in r["functions"]),
            "recovered_function_bodies": False,
            "modules": [{k: r[k] for k in ("module", "offset", "bytes", "constant_count", "functions")} for r in parsed],
        }
        output.mkdir(parents=True, exist_ok=True)
        (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n")
        for record in parsed:
            name = record["module"] or "__global__"
            (output / f"{name}.json").write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n")
        return summary
    raise DecodeError("No supported complete constant blob: " + "; ".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        summary = inspect(args.binary, args.output)
    except (OSError, DecodeError) as error:
        parser.exit(1, f"Analysis failed: {error}\n")
    print(json.dumps({k: summary[k] for k in ("sha256", "blob_offset", "module_count", "code_record_count", "function_count", "recovered_function_bodies")}, indent=2))


if __name__ == "__main__":
    main()
