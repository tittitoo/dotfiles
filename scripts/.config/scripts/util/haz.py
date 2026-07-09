"Parse and explain hazardous area equipment markings (ATEX / IECEx / Inmetro / NEC-CEC)."

import re
import shutil
import textwrap
import tomllib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# Terminals hard-wrap at the exact column width with no regard for word
# boundaries, so long single-line prose breaks mid-word. Wrap it ourselves at
# word boundaries instead, to the narrower of the actual terminal width (so a
# narrow terminal doesn't re-wrap our already-wrapped lines) or a comfortable
# reading-width cap (so a very wide terminal doesn't produce huge lines).
_MAX_WRAP_WIDTH = 96


def _wrap_width() -> int:
    return min(shutil.get_terminal_size(fallback=(_MAX_WRAP_WIDTH, 24)).columns, _MAX_WRAP_WIDTH)

CONFIG_PATH = Path(__file__).parent / "haz_config.toml"

with open(CONFIG_PATH, "rb") as _f:
    _DATA = tomllib.load(_f)

PROTECTION_TYPES = _DATA["protection_types"]
GAS_GROUPS = _DATA["gas_groups"]
DUST_GROUPS = _DATA["dust_groups"]
TEMP_CLASSES = _DATA["temp_classes"]
EPL = _DATA["epl"]
ZONES = _DATA["zones"]
NA_GROUPS = _DATA["na_groups"]
ATEX_GROUPS = _DATA["atex_groups"]
ATEX_CATEGORIES = _DATA["atex_categories"]
IP_SOLIDS = _DATA["ip_solids"]
IP_LIQUIDS = _DATA["ip_liquids"]

# Longest-code-first so greedy peeling doesn't stop at a shorter prefix
# (e.g. try "pxb" before "p" when peeling a compact token like "pxbia").
_PROTECTION_CODES_BY_LENGTH = sorted(PROTECTION_TYPES.keys(), key=len, reverse=True)

# "EEx" is the legacy CENELEC/pre-ATEX marking prefix (pre-2003), functionally
# identical to plain "Ex" — treated as a synonym so it isn't mistaken for two
# 'e' (increased safety) protection codes plus a stray leftover 'x'.
_IGNORED_TOKENS = {"ex", "eex", "group", "groups", "/"}

# EPL codes always follow this exact case pattern (G/D/M + lowercase a/b/c) in
# the standard, e.g. "Gb". Matching case-insensitively would collide with
# lowercase protection-type codes like "db" (flameproof) vs EPL "Db" (dust).
_EPL_PATTERN = re.compile(r"^[GDM][abc]$")

_CERT_PATTERNS = [
    ("IECEx", re.compile(r"\bIECEx\s+([A-Z]{2,5})\s+(\d{2}\.\d{4}[A-Z]?)\b", re.I)),
    ("ATEX", re.compile(r"\bCE\s?0?(\d{3,4})\b")),
    ("Inmetro", re.compile(r"\b(NCC|T[UÜ]V|UL-?BR)\s+(\d{2}\.\d{4}[A-Z]?)\b", re.I)),
    ("Inmetro", re.compile(r"\bPortaria\b", re.I)),
    ("Inmetro", re.compile(r"\bABNT\s*NBR\b", re.I)),
    ("NEC/CEC", re.compile(r"\bAEx\b")),
]

# Handles both plain "II 2G" and combined-category "II 2(1)G" forms — the
# latter means the main equipment is Category 2, paired with/incorporating
# Category 1 associated apparatus (common for IS systems with a barrier).
_ATEX_CATEGORY_RE = re.compile(
    r"\b(I{1,2})\s*([123])\s*(?:\(\s*([123])\s*\)\s*)?(GD|DG|G|D)\b"
)
_NEC_CLASS_DIV_RE = re.compile(r"\bClass\s+(I{1,3})\s*,?\s*Division\s+([12])\b", re.I)
_GAS_EXTENSION_RE = re.compile(r"\b(II[ABC])\s*\+\s*(H2|ACETYLENE)\b", re.I)

# Literal-Celsius temperature marking, common on dust ("t") equipment instead
# of/alongside a T-class letter code, e.g. "T135°C" or a dual rating
# "T135°C~T85°C" (max surface temp depends on ambient temperature range).
# Matched and removed BEFORE tokenizing so the leading "T" doesn't get
# mistaken for the legacy dust protection-type code "t".
_CELSIUS_TEMP_RE = re.compile(
    r"\bT\s*(\d{2,3})\s*°?\s*C(?:\s*[~-]\s*T?\s*(\d{2,3})\s*°?\s*C)?", re.I
)
_IP_RATING_RE = re.compile(r"\bIP\s?(\d|X)(\d|X|9K)\b", re.I)

# "op is"/"op pr"/"op sh" (optical radiation protection, IEC 60079-28) is
# written as two space-separated words. Joined into one token ("opis" etc.)
# before tokenizing so the peeler doesn't mistake bare "op" for the legacy
# 'o' (liquid immersion) + 'p' (pressurization) codes.
_OPTICAL_RADIATION_RE = re.compile(r"\bop\s+(is|pr|sh)\b", re.I)

_OCR_CONFUSABLE_ROMAN_RE = re.compile(r"^([Il|]{1,2})(?=\s*[123]\s*(?:\(|G|D))")

# For defuzzing mid-token Roman-numeral confusables, e.g. "lIC" -> "IIC".
_ROMAN_CONFUSABLES = str.maketrans({"L": "I", "|": "I", "1": "I"})


@dataclass
class ParseResult:
    canonical: str = ""
    protection_types: list = field(default_factory=list)
    gas_groups: list = field(default_factory=list)  # (group, extension|None)
    dust_groups: list = field(default_factory=list)
    temp_classes: list = field(default_factory=list)
    epls: list = field(default_factory=list)
    atex_category: str | None = None
    atex_group: str | None = None
    atex_category_primary: str | None = None
    atex_category_secondary: str | None = None
    atex_medium: str | None = None
    nec_class_division: str | None = None
    temp_classes_celsius: list = field(default_factory=list)  # (max_c, min_variant_c|None)
    ip_rating: str | None = None
    certificates: list = field(default_factory=list)  # (scheme, raw string)
    associated: "ParseResult | None" = None
    unrecognized: list = field(default_factory=list)
    scheme_guess: str = ""
    scheme_notes: list = field(default_factory=list)


def normalize(text: str) -> str:
    "Clean up common copy-paste/OCR artifacts before parsing."
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # ATEX Roman numeral "I"/"II" at the start of a marking, before the
    # category digit -- commonly OCR'd or copy-pasted (from image/PDF fonts
    # where I, l, and | are visually identical) as "l", "ll", "|", or "||".
    m = _OCR_CONFUSABLE_ROMAN_RE.match(text)
    if m:
        text = "I" * len(m.group(1)) + text[len(m.group(1)):]
    return text


def _extract_certificates(text: str) -> tuple[str, list[tuple[str, str]]]:
    found = []
    for scheme, pattern in _CERT_PATTERNS:
        for m in pattern.finditer(text):
            found.append((scheme, m.group(0)))
            text = text.replace(m.group(0), " ")
    return text, found


def _extract_atex_category(text: str) -> tuple[str, dict | None]:
    m = _ATEX_CATEGORY_RE.search(text)
    if not m:
        return text, None
    parsed = {
        "raw": re.sub(r"\s+", " ", m.group(0)).strip(),
        "group": m.group(1),
        "primary": m.group(2),
        "secondary": m.group(3),
        "medium": m.group(4),
    }
    return text.replace(m.group(0), " ", 1), parsed


def _extract_nec_class_division(text: str) -> tuple[str, str | None]:
    m = _NEC_CLASS_DIV_RE.search(text)
    if m:
        return text.replace(m.group(0), " ", 1), m.group(0)
    return text, None


def _extract_celsius_temps(text: str) -> tuple[str, list[tuple[str, str | None]]]:
    found = []
    for m in _CELSIUS_TEMP_RE.finditer(text):
        found.append((m.group(1), m.group(2)))
        text = text.replace(m.group(0), " ", 1)
    return text, found


def _extract_ip_rating(text: str) -> tuple[str, str | None]:
    m = _IP_RATING_RE.search(text)
    if m:
        return text.replace(m.group(0), " ", 1), f"IP{m.group(1)}{m.group(2)}".upper()
    return text, None


def _extract_brackets(text: str) -> tuple[str, str | None]:
    "Pull out one bracketed 'associated apparatus' rating, e.g. '[ia IIC Ga]'."
    m = re.search(r"\[([^\]]+)\]", text)
    if m:
        return text[: m.start()] + " " + text[m.end() :], m.group(1)
    return text, None


def _classify_token(token: str, na_context: bool = False) -> tuple[str, str] | None:
    """
    Classify a single already-split token. Returns (kind, canonical_value) or None.

    na_context gates single-letter NEC/CEC group matching (B, C, D, ...) so it
    only applies once a NEC/CEC marker (AEx, Class/Division) has already been
    detected elsewhere in the input — otherwise a bare "d" or "e" (legacy IEC
    protection-type codes) would be misread as NEC groups D/E.
    """
    upper = token.upper()
    # OCR/copy-paste often renders a Roman-numeral "I" in gas/dust group codes
    # (IIC, IIIA, ...) as "l", "|", or "1" — try a defuzzed match too.
    defuzzed = upper.translate(_ROMAN_CONFUSABLES)
    if upper in GAS_GROUPS:
        return ("gas_group", upper)
    if defuzzed in GAS_GROUPS:
        return ("gas_group", defuzzed)
    if upper in DUST_GROUPS:
        return ("dust_group", upper)
    if defuzzed in DUST_GROUPS:
        return ("dust_group", defuzzed)
    if upper in TEMP_CLASSES:
        return ("temp_class", upper)
    if _EPL_PATTERN.match(token) and token in EPL:
        return ("epl", token)
    if na_context and upper in NA_GROUPS and len(upper) == 1:
        return ("na_group", upper)
    return None


def _split_dual(token: str, na_context: bool = False) -> list[str]:
    "Split dual/alternate ratings joined with '/' or '~', e.g. 'T4/T6' or 'T4~T6'."
    sep = "/" if "/" in token else "~" if "~" in token else None
    if sep is None:
        return [token]
    parts = [p for p in token.split(sep) if p]
    if len(parts) > 1 and all(_classify_token(p, na_context) for p in parts):
        return parts
    return [token]


def _peel_protection_codes(token: str) -> tuple[list[str], str]:
    "Greedily peel known protection-type codes off the front of a compact token."
    matched = []
    remaining = token
    while remaining:
        for code in _PROTECTION_CODES_BY_LENGTH:
            if remaining.lower().startswith(code.lower()):
                matched.append(code.lower())
                remaining = remaining[len(code) :]
                break
        else:
            break
    return matched, remaining


def parse(raw_input: str) -> ParseResult:
    result = ParseResult()
    text = normalize(raw_input)

    text, result.certificates = _extract_certificates(text)
    text, atex_parsed = _extract_atex_category(text)
    if atex_parsed:
        result.atex_category = atex_parsed["raw"]
        result.atex_group = atex_parsed["group"]
        result.atex_category_primary = atex_parsed["primary"]
        result.atex_category_secondary = atex_parsed["secondary"]
        result.atex_medium = atex_parsed["medium"]
    text, result.nec_class_division = _extract_nec_class_division(text)
    na_context = bool(result.nec_class_division) or any(
        c[0] == "NEC/CEC" for c in result.certificates
    )
    text, result.temp_classes_celsius = _extract_celsius_temps(text)
    text, result.ip_rating = _extract_ip_rating(text)

    text, bracket_content = _extract_brackets(text)
    if bracket_content:
        result.associated = parse(bracket_content)

    # Normalize "IIB + H2" -> "IIB+H2" so it survives whitespace tokenizing as one token.
    text = _GAS_EXTENSION_RE.sub(lambda m: f"{m.group(1).upper()}+{m.group(2).upper()}", text)
    # Normalize "op is" -> "opis" for the same reason.
    text = _OPTICAL_RADIATION_RE.sub(lambda m: f"op{m.group(1).lower()}", text)

    for raw_token in text.split():
        token = raw_token.strip(",;")
        if not token:
            continue
        if token.lower() in _IGNORED_TOKENS:
            continue

        gas_ext_m = re.match(r"^(II[ABC])\+(H2|ACETYLENE)$", token, re.I)
        if gas_ext_m:
            result.gas_groups.append((gas_ext_m.group(1).upper(), gas_ext_m.group(2).upper()))
            continue

        classified_any = False
        for sub_token in _split_dual(token, na_context):
            classified = _classify_token(sub_token, na_context)
            if not classified:
                continue
            classified_any = True
            kind, value = classified
            if kind == "gas_group":
                result.gas_groups.append((value, None))
            elif kind == "dust_group":
                result.dust_groups.append(value)
            elif kind == "temp_class":
                result.temp_classes.append(value)
            elif kind == "epl":
                result.epls.append(value)
            elif kind == "na_group":
                result.protection_types.append(f"NEC-group-{value}")
        if classified_any:
            continue

        codes, leftover = _peel_protection_codes(token)
        if codes:
            result.protection_types.extend(codes)
            if leftover:
                result.unrecognized.append(leftover)
        else:
            result.unrecognized.append(token)

    result.canonical = build_canonical(result)
    result.scheme_guess, result.scheme_notes = infer_scheme(result)
    return result


def build_canonical(r: ParseResult) -> str:
    parts = []
    if r.atex_category:
        parts.append(r.atex_category)
    if r.nec_class_division:
        parts.append(r.nec_class_division)
    parts.append("Ex")
    parts.extend(
        PROTECTION_TYPES.get(code, {}).get("display", code) for code in r.protection_types
    )
    parts.extend(f"{g}+{ext}" if ext else g for g, ext in r.gas_groups)
    parts.extend(r.dust_groups)
    parts.extend(r.temp_classes)
    parts.extend(
        f"T{hi}°C~T{lo}°C" if lo else f"T{hi}°C" for hi, lo in r.temp_classes_celsius
    )
    parts.extend(r.epls)
    if r.ip_rating:
        parts.append(r.ip_rating)
    return " ".join(parts)


def infer_scheme(r: ParseResult) -> tuple[str, list[str]]:
    notes = []
    schemes_seen = {c[0] for c in r.certificates}
    if r.nec_class_division or "NEC/CEC" in schemes_seen:
        return "NEC/CEC (North American)", [
            "Detected an 'AEx' prefix or 'Class ... Division ...' phrase."
        ]

    matched = set(schemes_seen)
    if r.atex_category:
        matched.add("ATEX")

    if "IECEx" in matched:
        notes.append("Detected an IECEx certificate number (IECEx <body> YY.NNNN).")
    if "ATEX" in matched:
        notes.append("Detected an ATEX Category/Group prefix or CE+Notified-Body marker.")
    if "Inmetro" in matched:
        notes.append("Detected an Inmetro/ABNT NBR/Portaria/Brazilian-CB marker.")

    if len(matched) == 1:
        return next(iter(matched)), notes
    if len(matched) > 1:
        return " + ".join(sorted(matched)), notes
    return (
        "Ambiguous — ATEX, IECEx, and Inmetro all use this identical core marking",
        [
            "No scheme-specific marker found (ATEX Category/CE/Notified-Body, an IECEx "
            "certificate number, or an Inmetro/ABNT/Portaria reference). The 'Ex ...' "
            "string itself is identical across all three schemes."
        ],
    )


def _wrap(text: str, indent: str, hang: str = "") -> str:
    "Word-wrap a line of prose to the terminal width; continuation lines align flush with the first."
    wrapped = textwrap.wrap(
        text, width=_wrap_width(), initial_indent=indent, subsequent_indent=indent + hang
    )
    return "\n".join(wrapped) if wrapped else indent


def _epl_zone_line(epl_code: str) -> str:
    info = EPL.get(epl_code, {})
    zone = info.get("zone", "?")
    zone_info = ZONES.get(zone, {})
    if zone_info:
        return f"Zone {zone} — {zone_info.get('description', '')}"
    return f"Zone {zone}"


def _atex_category_lines(r: ParseResult, indent: str) -> list[str]:
    group_info = ATEX_GROUPS.get(r.atex_group, {})
    primary_info = ATEX_CATEGORIES.get(r.atex_category_primary, {})
    lines = [
        f"{indent}ATEX Group/Category: {r.atex_category}",
        _wrap(f"Group {r.atex_group}: {group_info.get('plain', '')}", indent + "  "),
        _wrap(
            f"Category {r.atex_category_primary}: {primary_info.get('plain', '')}",
            indent + "  ",
        ),
    ]
    if r.atex_category_secondary:
        secondary_info = ATEX_CATEGORIES.get(r.atex_category_secondary, {})
        lines.append(
            _wrap(
                f"Combined with Category {r.atex_category_secondary} associated "
                f"apparatus: {secondary_info.get('plain', '')} (common for "
                f"intrinsically-safe equipment paired with a safety barrier)",
                indent + "  ",
            )
        )
    medium_names = {"G": "Gas", "D": "Dust", "GD": "Gas and Dust", "DG": "Gas and Dust"}
    lines.append(
        f"{indent}  Medium: {r.atex_medium} — {medium_names.get(r.atex_medium, r.atex_medium)}"
    )
    return lines


def explain(r: ParseResult, indent: str = "") -> str:
    lines = []
    lines.append(f"{indent}Canonical marking: {r.canonical}")
    lines.append(_wrap(f"Certification scheme: {r.scheme_guess}", indent))
    for note in r.scheme_notes:
        lines.append(_wrap(f"- {note}", indent + "  "))

    if r.atex_group:
        lines.append(f"{indent}")
        lines.extend(_atex_category_lines(r, indent))

    if r.protection_types:
        lines.append(f"{indent}")
        lines.append(f"{indent}Type(s) of protection:")
        for code in r.protection_types:
            if code.startswith("NEC-group-"):
                letter = code.removeprefix("NEC-group-")
                info = NA_GROUPS.get(letter, {})
                lines.append(
                    _wrap(
                        f"Group {letter} ({info.get('medium', '?')}) — "
                        f"example: {info.get('example_gas', '?')}; approx. IEC equivalent: "
                        f"{info.get('iec_equivalent_approx', '?')} (approximate, not a "
                        f"strict legal equivalence)",
                        indent + "  ",
                    )
                )
                continue
            info = PROTECTION_TYPES.get(code)
            if not info:
                lines.append(f"{indent}  {code} — unrecognized protection-type code")
                continue
            display = info.get("display", code)
            lines.append(
                _wrap(f"{display} — {info['name']} ({info.get('standard', '')})", indent + "  ")
            )
            lines.append(_wrap(info["description"], indent + "    "))
            if info.get("plain"):
                lines.append(_wrap(f"In plain terms: {info['plain']}", indent + "    "))
            if info.get("notes"):
                lines.append(_wrap(f"Note: {info['notes']}", indent + "    "))
            epl_code = info.get("epl")
            if epl_code:
                lines.append(
                    _wrap(
                        f"Normally paired with EPL {epl_code} -> {_epl_zone_line(epl_code)}",
                        indent + "    ",
                    )
                )

    if r.gas_groups:
        lines.append(f"{indent}")
        lines.append(f"{indent}Gas group(s):")
        for group, ext in r.gas_groups:
            info = GAS_GROUPS.get(group, {})
            suffix = f" + {ext}" if ext else ""
            lines.append(
                f"{indent}  {group}{suffix} — {info.get('name', '')}; "
                f"example gas: {info.get('example_gas', '?')}"
            )
            if info.get("plain"):
                lines.append(_wrap(f"In plain terms: {info['plain']}", indent + "    "))
            if info.get("note"):
                lines.append(_wrap(info["note"], indent + "    "))
            if ext:
                lines.append(
                    _wrap(
                        f"'+{ext}' denotes additional testing/rating specific to that "
                        f"gas beyond the base group.",
                        indent + "    ",
                    )
                )

    if r.dust_groups:
        lines.append(f"{indent}")
        lines.append(f"{indent}Dust group(s):")
        for group in r.dust_groups:
            info = DUST_GROUPS.get(group, {})
            lines.append(f"{indent}  {group} — {info.get('description', '')}")
            if info.get("plain"):
                lines.append(_wrap(f"In plain terms: {info['plain']}", indent + "    "))
            if info.get("note"):
                lines.append(_wrap(info["note"], indent + "    "))

    if r.temp_classes:
        lines.append(f"{indent}")
        lines.append(f"{indent}Temperature class(es):")
        for t in r.temp_classes:
            info = TEMP_CLASSES.get(t, {})
            lines.append(f"{indent}  {t} — max surface temperature {info.get('max_surface_c', '?')} degC")
        if len(r.temp_classes) > 1:
            lines.append(
                _wrap(
                    "Multiple T-classes means the achievable rating depends on the "
                    "ambient temperature the equipment is installed in — a higher "
                    "surface temp (e.g. T4) is guaranteed across a wider ambient "
                    "range, while a lower/cooler surface temp (e.g. T6) only holds "
                    "within a narrower ambient range. Check the certificate's "
                    "Ta-vs-T-class table for which one applies at your site; don't "
                    "assume the coolest-rated class applies everywhere.",
                    indent + "  ",
                )
            )

    if r.temp_classes_celsius:
        lines.append(f"{indent}")
        lines.append(f"{indent}Temperature rating(s) (literal, not a T-class letter code):")
        for hi, lo in r.temp_classes_celsius:
            if lo:
                lines.append(
                    _wrap(
                        f"T{hi}C ~ T{lo}C — max surface temperature ranges from {hi} degC "
                        f"down to {lo} degC depending on the ambient temperature range the "
                        f"equipment is rated for (check the certificate for which ambient "
                        f"range applies to which surface temp).",
                        indent + "  ",
                    )
                )
            else:
                lines.append(f"{indent}  T{hi}C — max surface temperature {hi} degC")

    if r.ip_rating:
        lines.append(f"{indent}")
        digits = r.ip_rating.removeprefix("IP")
        solid_digit, liquid_digit = digits[0], digits[1:]
        solid_info = IP_SOLIDS.get(solid_digit, {})
        liquid_info = IP_LIQUIDS.get(liquid_digit, {})
        lines.append(f"{indent}Ingress Protection (IP) rating: {r.ip_rating}")
        lines.append(
            _wrap(f"Solids/dust ({solid_digit}): {solid_info.get('plain', '?')}", indent + "  ")
        )
        lines.append(
            _wrap(f"Liquids/water ({liquid_digit}): {liquid_info.get('plain', '?')}", indent + "  ")
        )

    if r.epls:
        lines.append(f"{indent}")
        lines.append(f"{indent}Equipment Protection Level(s):")
        for e in r.epls:
            info = EPL.get(e, {})
            lines.append(
                _wrap(
                    f"{e} — {info.get('description', '')} ({_epl_zone_line(e)})",
                    indent + "  ",
                )
            )
            if info.get("plain"):
                lines.append(_wrap(f"In plain terms: {info['plain']}", indent + "    "))

    if r.associated:
        lines.append(f"{indent}")
        lines.append(f"{indent}Associated apparatus rating (bracketed portion):")
        lines.append(explain(r.associated, indent=indent + "  "))

    if r.certificates:
        lines.append(f"{indent}")
        lines.append(f"{indent}Certificate reference(s) found in input:")
        for scheme, raw in r.certificates:
            lines.append(f"{indent}  {scheme}: {raw}")

    if r.unrecognized:
        lines.append(f"{indent}")
        lines.append(f"{indent}Could not classify (check for typos):")
        for u in r.unrecognized:
            lines.append(f"{indent}  {u}")

    return "\n".join(lines)
