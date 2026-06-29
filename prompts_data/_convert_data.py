"""One-shot converter: prompt-bible/data.js → prompts.json.

The source file is a JavaScript object literal that gets assigned to
`window.PROMPT_BIBLE`. To make it readable from Python we:

  1. Strip the `window.PROMPT_BIBLE = ` prefix and trailing `;`.
  2. Drop `//` line comments and `/* block */` comments (string-aware:
     never strip inside string literals).
  3. Escape raw control chars (\\n / \\r / \\t) inside string literals
     so JSON-parsing succeeds. data.js has a few multi-line strings
     and embedded comment markers inside strings.
  4. Convert every `[...].join("<sep>")` block (used by `prompt:` and
     `variants.<model>`) into a plain quoted string by joining the
     array entries with the separator.
  5. Quote unquoted object keys (`{ id: ... }` -> `{"id": ...}`).
  6. Convert JS literals (`true` / `false` / `null` / `undefined`).
  7. JSON-parse the result.

Run:  python3 _convert_data.py
Writes: prompts.json next to this script.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path("/Users/zero/Minimax Projects/prompt-bible/data.js")
DST = Path(__file__).parent / "prompts.json"


def strip_comments(src: str) -> str:
    """Drop JS line + block comments, but NOT inside string literals.
    Some prompt entries legitimately contain `//` markers inside
    strings (e.g. a `// @ts-nocheck` reference) — we must preserve those.
    """
    out: list[str] = []
    i = 0
    n = len(src)
    in_str: "str | None" = None
    while i < n:
        c = src[i]
        if in_str:
            if c == "\\" and i + 1 < n:
                out.append(c)
                out.append(src[i + 1])
                i += 2
                continue
            if c == in_str:
                in_str = None
            out.append(c)
            i += 1
            continue
        if c == '"' or c == "'" or c == "`":
            in_str = c
            out.append(c)
            i += 1
            continue
        # Block comment /* ... */ (multiline)
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            j = src.find("*/", i + 2)
            if j == -1:
                break  # unterminated — bail
            i = j + 2
            continue
        # Line comment // ... (until newline)
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i + 2)
            if j == -1:
                break
            i = j  # keep newline, drop comment
            continue
        out.append(c)
        i += 1
    return "".join(out)


def strip_orphan_comment_commas(src: str) -> str:
    """Pre-pass: data.js sometimes writes `,\\n// divider comment\\n`
    between prompts — the SECOND `,` is only there because the comment
    is on its own line. Drop it (string-aware: never touch a `,` inside
    a string literal).

    Heuristic: a `,` is an orphan iff:
      - the previous non-whitespace character is also a terminator
        (`,` `}` `]`), AND
      - the next non-whitespace content is a `//` line comment (or end
        of file).
    """
    out: list[str] = []
    i = 0
    n = len(src)
    in_str: "str | None" = None
    while i < n:
        c = src[i]
        if in_str:
            if c == "\\" and i + 1 < n:
                out.append(c)
                out.append(src[i + 1])
                i += 2
                continue
            if c == in_str:
                in_str = None
            out.append(c)
            i += 1
            continue
        if c == '"' or c == "'" or c == "`":
            in_str = c
            out.append(c)
            i += 1
            continue
        if c == ",":
            # Look back through `out` for the previous non-whitespace char.
            k = len(out) - 1
            while k >= 0 and out[k] in (" ", "\t", "\n", "\r"):
                k -= 1
            prev = out[k] if k >= 0 else ""
            # Look forward through `src` for the next non-whitespace char.
            j = i + 1
            while j < n and src[j] in (" ", "\t", "\n", "\r"):
                j += 1
            nxt = src[j] if j < n else ""
            # Orphan iff prev-was-also-comma AND next-is-comment-or-eof.
            # We require prev == "," (not "}" or "]") because:
            #   `},\n,\n//comment`  -> the second `,` is orphan (prev is `,`)
            #   `},\n//comment`    -> the `,` is the real separator
            #                            (prev is `}`), so keep it.
            if prev == "," and (nxt == "" or (nxt == "/" and j + 1 < n and src[j + 1] == "/")):
                i += 1
                continue
        out.append(c)
        i += 1
    return "".join(out)


def escape_string_newlines(src: str) -> str:
    """Replace raw newlines/tabs inside double-quoted strings with their
    escape sequences. data.js has a few string literals with literal
    newlines (constraints list inside antiPatterns). JSON does not allow
    raw control chars in strings, so we fix them up here.
    """
    out: list[str] = []
    i = 0
    n = len(src)
    in_str: "str | None" = None
    while i < n:
        c = src[i]
        if in_str:
            if c == "\\" and i + 1 < n:
                out.append(c)
                out.append(src[i + 1])
                i += 2
                continue
            if c == "\n":
                out.append("\\n")
                i += 1
                continue
            if c == "\r":
                out.append("\\r")
                i += 1
                continue
            if c == "\t":
                out.append("\\t")
                i += 1
                continue
            if c == in_str:
                in_str = None
            out.append(c)
            i += 1
            continue
        if c == '"' or c == "'" or c == "`":
            in_str = c
        out.append(c)
        i += 1
    return "".join(out)


def evaluate_array_join(src: str) -> str:
    """Find every `[...].join(<sep>)` block and replace each with the
    joined result as a JSON-escaped string. Walks the source left-to-right
    and finds each `[` whose matching `]` is followed by `.join(...)`.
    This covers both `prompt: [...]` and `variants: { model: [...] }`.
    Tracks bracket + string depth so an unbalanced `[`/`]` inside a
    string doesn't break the count.
    """
    out: list[str] = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c != "[":
            out.append(c)
            i += 1
            continue
        # Found a `[`. Walk forward to its matching `]`.
        start = i
        j = i + 1
        depth = 1
        in_str: "str | None" = None
        while j < n and depth > 0:
            cc = src[j]
            if in_str:
                if cc == "\\" and j + 1 < n:
                    j += 2
                    continue
                if cc == in_str:
                    in_str = None
                j += 1
                continue
            if cc in ('"', "'", "`"):
                in_str = cc
            elif cc == "[":
                depth += 1
            elif cc == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        # src[j] is the matching `]`.
        tail = src[j + 1 :]
        join_match = re.match(
            r"\s*\.\s*join\s*\(\s*(['\"])(.*?)\1\s*\)\s*(,?)",
            tail,
            re.DOTALL,
        )
        if not join_match:
            # Not a `[...].join(...)`; keep `[` and continue.
            out.append(c)
            i += 1
            continue
        sep = join_match.group(2)
        trailing = join_match.group(3)
        array_inner = src[i + 1 : j]
        try:
            arr = json.loads(f"[{array_inner}]")
        except json.JSONDecodeError:
            # Couldn't parse the array; emit raw and skip.
            out.append(src[start : j + 1 + join_match.end()])
            i = j + 1 + join_match.end()
            continue
        joined = sep.join(arr)
        out.append(json.dumps(joined, ensure_ascii=False))
        out.append(trailing)
        i = j + 1 + join_match.end()
    return "".join(out)


def quote_unquoted_keys(src: str) -> str:
    """Quote object keys that were left bare in JS object literals.
    `{ foo: 1, bar: 2 }` -> `{ "foo": 1, "bar": 2 }`. String-aware:
    never touch content inside string literals.
    """
    out: list[str] = []
    i = 0
    n = len(src)
    in_str: "str | None" = None
    while i < n:
        c = src[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(src[i + 1])
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ('"', "'", "`"):
            in_str = c
            out.append(c)
            i += 1
            continue
        # Look for an identifier-or-quoted-string followed by `:`.
        m = re.match(r"[A-Za-z_$][\w$\-]*", src[i:])
        if m and i + m.end() < n and src[i + m.end()] == ":":
            if m.group(0) not in {"true", "false", "null", "undefined"}:
                out.append('"' + m.group(0) + '"')
                i += m.end()
                continue
        out.append(c)
        i += 1
    return "".join(out)


def js_literals_to_json(src: str) -> str:
    src = re.sub(r"\btrue\b", "true", src)
    src = re.sub(r"\bfalse\b", "false", src)
    src = re.sub(r"\bnull\b", "null", src)
    src = re.sub(r"\bundefined\b", "null", src)
    return src


def main() -> int:
    raw = SRC.read_text(encoding="utf-8")

    # 1. Trim prefix/suffix to leave the bare object literal.
    m = re.search(r"window\.PROMPT_BIBLE\s*=\s*", raw)
    if not m:
        print("ERROR: could not locate `window.PROMPT_BIBLE = ` assignment", file=sys.stderr)
        return 1
    body = raw[m.end():].rstrip()
    if body.endswith(";"):
        body = body[:-1]

    # 2. Drop orphan commas that exist only to separate divider comments.
    body = strip_orphan_comment_commas(body)

    # 3. Drop comments (string-aware).
    body = strip_comments(body)

    # 3. Escape raw control chars inside string literals.
    body = escape_string_newlines(body)

    # 4. Convert every [...].join(...) into a joined string.
    body = evaluate_array_join(body)

    # 5. JS literal aliases (no-op for true/false/null, kept explicit).
    body = js_literals_to_json(body)

    # 6. Quote bare object keys.
    body = quote_unquoted_keys(body)

    # 7. JSON-parse.
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        debug_path = DST.with_suffix(".debug.json")
        debug_path.write_text(body, encoding="utf-8")
        print(f"ERROR: JSON parse failed at line {e.lineno}, col {e.colno}: {e.msg}", file=sys.stderr)
        print(f"  Debug dump -> {debug_path}", file=sys.stderr)
        return 1

    if "prompts" not in data or not isinstance(data["prompts"], list):
        print("ERROR: converted data has no `prompts` array", file=sys.stderr)
        return 1
    print(f"OK: {len(data['prompts'])} prompts parsed", file=sys.stderr)

    DST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote: {DST} ({DST.stat().st_size / 1024:.1f} KB)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())