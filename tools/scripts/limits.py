"""Text-window limits (visible characters per line, lines per page) by game file group and dialog kind.

Derived from the EN original (99th percentile of line length / page height per group, see
docs/translation_guide.md). Character counts are a proxy until the Cyrillic font metrics are known
(stage 5); then these numbers get re-tuned to pixel widths.
"""

# (group prefix, kind) -> (max chars per line, max lines per page); first match wins
RULES = [
    (("EN/INIT/DATMSG.PAK", "msg"), (49, 10)),   # item/skill descriptions
    (("EN/FACILITY", "msg"), (49, 10)),          # shop descriptions
    (("EN/TUTORIAL", "msg"), (55, 4)),
    (("EN/FIELD/OBJECT_HIT", "msg"), (16, 1)),   # short field labels
    (("", "sel"), (32, 1)),                      # selection options
    (("", "msg"), (44, 3)),                      # dialogue window
]
HARD_EXTRA = 2  # lines up to limit+2 are warnings; more is an error


def limit_for(file, kind):
    for (prefix, k), lim in RULES:
        if file.startswith(prefix) and kind == k:
            return lim
    return 44, 3
