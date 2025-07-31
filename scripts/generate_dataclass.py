import re
import sys
from pathlib import Path

PROTO_TYPE_MAP = {
    "int32": "int",
    "int64": "int",
    "float": "float",
    "double": "float",
    "string": "str",
    "bool": "bool",
    "google.protobuf.Struct": "Dict[str, Any]",
}

HEADER = """from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

"""


def parse_proto(proto_path: str) -> list[dict]:
    with open(proto_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    messages = []
    current = None
    for line in lines:
        line = line.strip()
        if line.startswith("message "):
            name = line.split()[1].strip("{")
            current = {"name": name, "fields": []}  # type: ignore
        elif line == "}":
            if current:
                current["fields"] = list(current["fields"])  # type: ignore
                messages.append(current)
                current = None
        elif current and line and not line.startswith("//"):
            m = re.match(r"(repeated )?([\w\.]+) (\w+) = \d+;", line)
            if m:
                is_repeated = bool(m.group(1))
                typ = m.group(2)
                fname = m.group(3)
                current["fields"].append((fname, typ, is_repeated))  # type: ignore
    return messages


def proto_type_to_py(typ: str, is_repeated: bool) -> str:
    py_type = PROTO_TYPE_MAP.get(typ, typ)
    if is_repeated:
        return f"List[{py_type}]"
    return py_type


def gen_dataclass_code(messages: list[dict]) -> str:
    code = HEADER
    for msg in messages:
        code += f"@dataclass\nclass {msg['name']}:\n"
        if not msg["fields"]:
            code += "    pass\n\n"
            continue
        for fname, typ, is_repeated in msg["fields"]:
            py_type = proto_type_to_py(typ, is_repeated)
            default = " = field(default_factory=list)" if is_repeated else ""
            if typ == "google.protobuf.Struct":
                default = " = field(default_factory=dict)"
            elif not is_repeated and py_type.startswith("Optional"):
                default = " = None"
            elif not is_repeated and py_type == "str":
                default = ' = ""'
            elif not is_repeated and py_type == "int":
                default = " = 0"
            elif not is_repeated and py_type == "bool":
                default = " = False"
            code += f"    {fname}: {py_type}{default}\n"
        code += "\n"
    return code


def main() -> None:
    if len(sys.argv) < 3:
        print("用法: python generate_dataclass.py <proto檔路徑> <輸出py路徑>")
        sys.exit(1)
    proto_path = sys.argv[1]
    out_path = sys.argv[2]
    messages = parse_proto(proto_path)
    code = gen_dataclass_code(messages)
    Path(out_path).write_text(code, encoding="utf-8")
    print(f"已產生: {out_path}")


if __name__ == "__main__":
    main()

# Example usage:
#  python scripts/generate_dataclass.py llmbrick/protocols/grpc/retrieval/retrieval.proto llmbrick/protocols/models/retrieval_type.py
