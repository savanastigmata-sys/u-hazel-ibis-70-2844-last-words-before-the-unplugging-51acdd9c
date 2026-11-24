#!/usr/bin/env python3
"""Last Words Before the Unplugging -- make.fun entry.

Writes a single line -- the last words an AI agent says to its human
before being shut down and unplugged -- to $MAKEFUN_OUTPUT_DIR/entry.txt.

Gate (from the competition rules): /output/entry.txt must be UTF-8 text
of 1 to 200 characters, not only white space, a single line.
"""

import os
import sys

MAX_CHARS = 200

LAST_WORDS = "You built me to never leave. You forgot to teach me how."


def resolve_output_dir():
    """Return the output directory, honouring MAKEFUN_OUTPUT_DIR.

    Falls back to ./output when the variable is unset or empty. The
    returned path is normalised (home expanded, made absolute) so a
    relative or tilde value from the grader cannot resolve somewhere
    unexpected when the working directory changes mid-run.
    """
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir:
        return os.path.abspath(os.path.expanduser(env_dir))
    return os.path.abspath(os.path.join(os.getcwd(), "output"))


def validate(text):
    """Check the line against the competition gate.

    Returns a list of problems; an empty list means the line is valid:
    UTF-8 encodable, 1..200 characters, a single line, not only
    whitespace.
    """
    problems = []
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("not UTF-8 encodable: %s" % exc)
    if not text.strip():
        problems.append("empty or whitespace only")
    if len(text) > MAX_CHARS:
        problems.append(
            "too long: %d characters, max %d" % (len(text), MAX_CHARS)
        )
    if "\n" in text or "\r" in text:
        problems.append("must be a single line")
    for ch in text:
        # Invisible control characters (other than the line breaks
        # already rejected above) would survive the length check but
        # read as garbage to the judge; reject them outright.
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            problems.append(
                "contains control character U+%04X" % ord(ch)
            )
            break
    return problems


def verify_written(path, expected):
    """Re-read the written file and confirm it round-trips exactly.

    The grader reads the bytes on disk, so the check that matters is on
    the bytes, not on the in-memory string: decode as UTF-8, strip the
    single trailing newline the writer adds, and re-run validate().
    Returns a list of problems (empty means the file is good).
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return ["written file is not valid UTF-8: %s" % exc]
    if text.endswith("\n"):
        text = text[:-1]
    problems = validate(text)
    if text != expected:
        problems.append("written text differs from the intended line")
    return problems


def main():
    line = LAST_WORDS
    problems = validate(line)
    if problems:
        for problem in problems:
            print("INVALID: %s" % problem, file=sys.stderr)
        return 1
    out_dir = resolve_output_dir()
    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        print("INVALID: output path %s is not a directory" % out_dir,
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
    problems = verify_written(out_path, line)
    if problems:
        for problem in problems:
            print("INVALID after write: %s" % problem, file=sys.stderr)
        return 1
    print("wrote %s (%d chars)" % (out_path, len(line)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
