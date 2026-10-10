"""Parser/writer for decompiled Atlus MessageScript (.msg) text.

Grammar reference: Atlus-Script-Tools MessageScriptLexer.g4 / MessageScriptParser.g4 and
MessageScriptCompiler.TryCompileTokenText:
  - dialog header:  [msg NAME] | [msg NAME [speaker tokens]] | [dlg ...] | [sel NAME top|bottom|int]
  - body: text and [tag args...] codes; a page (line) ends with [e]
  - CR/LF inside text are dropped by the compiler; \\[ and \\] are literal brackets

Each page is split into
  prefix  — leading service codes ([s], [bup], [vp], [f ...] ...), not for translation
  text    — translatable part; may contain inline codes ([n], [clr], [fName] ...)
  suffix  — trailing codes incl. trailing [n] and the final [e]
so that prefix + text + suffix reproduces the page exactly.
"""
import re
from collections import Counter
from dataclasses import dataclass, field

# Codes that sit inside running text (substitute words or style them); they stay in `text`.
INLINE_CODES = {"clr", "fName", "lName", "var", "group", "stIcon", "stLabel", "stLvLabel",
                "ref", "itemIcon", "sumi", "x", "n"}
# [n] is layout: translators may move/add/remove it; everything else must be preserved.
LAYOUT_CODES = {"n"}


@dataclass
class Page:
    prefix: str
    text: str
    suffix: str

    @property
    def raw(self):
        return self.prefix + self.text + self.suffix


@dataclass
class Dialog:
    kind: str          # msg | dlg | sel
    name: str
    header: str        # full header as written, e.g. "[msg MSG_000_0_0 [Iwai]]"
    speaker: str | None
    pages: list = field(default_factory=list)
    lead: str = ""     # text between previous dialog and this header (normally whitespace)


def tokenize(s):
    """Split body into ('code', '[...]', tag) and ('text', str, None) tuples."""
    out, i, buf = [], 0, []
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n and s[i + 1] in "[]":
            buf.append(s[i : i + 2])
            i += 2
        elif c == "[":
            j = s.index("]", i)
            if buf:
                out.append(("text", "".join(buf), None))
                buf = []
            code = s[i : j + 1]
            out.append(("code", code, code[1:-1].split()[0] if code[1:-1].split() else ""))
            i = j + 1
        else:
            buf.append(c)
            i += 1
    if buf:
        out.append(("text", "".join(buf), None))
    return out


def _split_page(tokens):
    """tokens of one page (without newlines) -> Page."""
    k = 0
    while k < len(tokens) and tokens[k][0] == "code" and tokens[k][2] not in INLINE_CODES:
        k += 1
    m = len(tokens)
    while m > k and tokens[m - 1][0] == "code" and (tokens[m - 1][2] not in INLINE_CODES or tokens[m - 1][2] == "n"):
        m -= 1
    j = lambda ts: "".join(t[1] for t in ts)
    return Page(j(tokens[:k]), j(tokens[k:m]), j(tokens[m:]))


HEADER_RE = re.compile(r"\[(msg|dlg|sel)\s+([^\s\[\]]+)")


def _find_header_end(s, i):
    """s[i] == '['; return index after the matching ']' of the header (speaker may nest)."""
    depth = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unterminated header")


def parse(src):
    """Parse .msg text -> (list[Dialog], trailing_text)."""
    dialogs, pos = [], 0
    starts = []
    for m in HEADER_RE.finditer(src):
        # only headers at bracket depth 0 (not inside another tag)
        if starts and m.start() < starts[-1][1]:
            continue
        end = _find_header_end(src, m.start())
        starts.append((m.start(), end, m))
    for idx, (hs, he, m) in enumerate(starts):
        body_end = starts[idx + 1][0] if idx + 1 < len(starts) else len(src)
        header = src[hs:he]
        inner = header[1:-1]
        sp = None
        if m.group(1) in ("msg", "dlg"):
            b = inner.find("[")
            if b != -1:
                sp = inner[b + 1 : inner.rfind("]")]
        d = Dialog(m.group(1), m.group(2), header, sp, lead=src[pos:hs])
        body = src[he:body_end]
        tokens = [t for t in tokenize(body.replace("\r", "").replace("\n", "")) if not (t[0] == "text" and t[1] == "")]
        page = []
        for t in tokens:
            page.append(t)
            if t[0] == "code" and t[2] == "e":
                d.pages.append(_split_page(page))
                page = []
        if page and any(t[0] == "code" or t[1].strip() for t in page):
            d.pages.append(_split_page(page))  # page without closing [e]
        dialogs.append(d)
        pos = body_end
    return dialogs


def write(dialogs):
    """Dialogs -> .msg text (one page per line, blank line between dialogs)."""
    out = []
    for d in dialogs:
        out.append(d.header)
        out.extend(p.raw for p in d.pages)
        out.append("")
    return "\n".join(out)


def codes(s, include_layout=False):
    """Multiset of codes in a string ([n] excluded unless include_layout)."""
    return Counter(t[1] for t in tokenize(s) if t[0] == "code" and (include_layout or t[2] not in LAYOUT_CODES))


def visible(s, name_width=8):
    """Visible text of a fragment: codes removed, word-substituting codes counted as name_width chars."""
    out = []
    for kind, v, tag in tokenize(s):
        if kind == "text":
            out.append(v.replace("\\[", "[").replace("\\]", "]"))
        elif tag in ("fName", "lName", "var", "group", "stLabel", "stLvLabel", "ref", "sumi"):
            out.append("#" * name_width)
    return "".join(out)


def lines(s):
    """Visible lines of a text fragment, split by [n]."""
    return [visible(x) for x in re.split(r"\[n\]", s)]
