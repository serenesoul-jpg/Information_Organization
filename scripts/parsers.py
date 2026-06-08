"""解析 CSV 经典篇目、别称等字段。"""
import re


def clean_text(value) -> str:
    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return ""
    text = str(value).strip()
    return re.sub(r"\[__LINK_ICON\]", "", text).strip()


def split_aliases(alias_text: str, cipai_name: str) -> list[str]:
    if not alias_text:
        return []
    aliases = []
    for part in re.split(r"[、，,]", alias_text):
        name = part.strip()
        if not name or name == cipai_name:
            continue
        if name not in aliases:
            aliases.append(name)
    return aliases


def parse_classic_works(classic_text: str) -> list[dict]:
    """解析经典篇目，支持「词人《标题》」及分号分隔的多篇。"""
    text = clean_text(classic_text)
    if not text:
        return []

    works = []
    for part in re.split(r"[；;]", text):
        part = part.strip()
        if not part:
            continue

        match = re.match(r"^(.+?)《(.+?)》(.*)$", part)
        if match:
            poet = match.group(1).strip()
            title = match.group(2).strip()
            extra = match.group(3).strip()
            if extra.startswith(("：", ":")):
                extra = extra[1:].strip()
            works.append({"poet": poet, "title": title, "note": extra})
        else:
            works.append({"poet": "", "title": part, "note": ""})

    return works
