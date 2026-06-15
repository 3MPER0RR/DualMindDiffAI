def load_file(path: str) -> str:
    if not path:
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
