import difflib

def diff(a: str, b: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            a.splitlines(),
            b.splitlines(),
            fromfile="SAFE",
            tofile="RAW",
            lineterm=""
        )
    )
