"""Gantt chart generation from markdown schedule files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path


@dataclass
class Item:
    name: str
    lead_min: int
    lead_max: int
    origin: str | None = None
    is_milestone: bool = False
    freight_weeks: int = 0  # sea freight buffer; computed from origin at parse time


def _calc_freight(origin: str | None) -> int:
    """Return sea freight weeks based on origin country code.

    CN → 2 weeks (short sea), all other non-SG origins → 4 weeks (long haul).
    """
    if not origin:
        return 0
    country = origin.upper().split()[-1]
    if country == "SG":
        return 0
    if country == "CN":
        return 2
    return 4  # 3–4 wks long-haul, use max for conservative scheduling


@dataclass
class Phase:
    name: str
    items: list[Item] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    fixed_start: int | None = None  # [start: WK15] → 15; overrides / floors dependency calc
    start_week: int = 0
    end_week: int = 0


@dataclass
class Schedule:
    project_name: str
    start_date: date
    phases: list[Phase] = field(default_factory=list)


_LEAD_RANGE_RE  = re.compile(r":\s*(\d+)\s*[–\-]\s*(\d+)\s*wks?(.*)$", re.IGNORECASE)
_LEAD_SINGLE_RE = re.compile(r":\s*(\d+)\s*wks?(.*)$", re.IGNORECASE)
_AFTER_RE       = re.compile(r"\[after:\s*([^\]]+)\]", re.IGNORECASE)
_PHASE_START_RE = re.compile(r"\[start:\s*(?:WK)?(\d+)\]", re.IGNORECASE)
_START_RE       = re.compile(r"^start:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)


def parse_schedule(md_text: str) -> Schedule:
    phases: list[Phase] = []
    project_name = ""
    start_date = date.today()
    current_phase: Phase | None = None

    for line in md_text.splitlines():
        s = line.strip()

        if s.startswith("# ") and not s.startswith("## "):
            project_name = s[2:].strip()
            continue

        m = _START_RE.match(s)
        if m:
            start_date = date.fromisoformat(m.group(1))
            continue

        if s.startswith("## "):
            content = s[3:].strip()
            depends: list[str] = []
            fixed_start: int | None = None
            # Parse [start: WKN] first so [after:] doesn't consume it
            ps_m = _PHASE_START_RE.search(content)
            if ps_m:
                fixed_start = int(ps_m.group(1)) - 1  # convert 1-based WK to 0-based
                content = (content[: ps_m.start()] + content[ps_m.end():]).strip()
            after_m = _AFTER_RE.search(content)
            if after_m:
                depends = [d.strip() for d in after_m.group(1).split(",")]
                content = content[: after_m.start()].strip()
            current_phase = Phase(name=content, depends_on=depends, fixed_start=fixed_start)
            phases.append(current_phase)
            continue

        if s.startswith("- ") and current_phase is not None:
            text = s[2:].strip()

            if text.lower().startswith("milestone:"):
                milestone_name = text[len("milestone:"):].strip()
                current_phase.items.append(
                    Item(name=milestone_name, lead_min=0, lead_max=0, is_milestone=True)
                )
                continue

            m2 = _LEAD_RANGE_RE.search(text)
            if m2:
                lead_min, lead_max = int(m2.group(1)), int(m2.group(2))
                origin = m2.group(3).strip() or None
                name = text[: m2.start()].strip()
            else:
                m3 = _LEAD_SINGLE_RE.search(text)
                if m3:
                    lead_min = lead_max = int(m3.group(1))
                    origin = m3.group(2).strip() or None
                    name = text[: m3.start()].strip()
                else:
                    name, lead_min, lead_max, origin = text, 0, 0, None

            current_phase.items.append(
                Item(name=name, lead_min=lead_min, lead_max=lead_max,
                     origin=origin, freight_weeks=_calc_freight(origin))
            )

    return Schedule(project_name=project_name, start_date=start_date, phases=phases)


def _compute_schedule(phases: list[Phase]) -> None:
    by_name = {p.name: p for p in phases}
    for i, phase in enumerate(phases):
        if phase.fixed_start is not None and not phase.depends_on:
            # [start: WKN] with no [after:] → hard override; ignore implicit prev-phase sequencing
            phase.start_week = phase.fixed_start
        elif phase.depends_on:
            deps = [by_name[d] for d in phase.depends_on if d in by_name]
            dep_end = max((d.end_week for d in deps), default=0)
            # [after: X] [start: WKN] → later of dependency end or fixed floor
            phase.start_week = max(dep_end, phase.fixed_start) if phase.fixed_start is not None else dep_end
        else:
            # No annotation → sequential after previous phase
            phase.start_week = 0 if i == 0 else phases[i - 1].end_week

        max_lead = max(
            (item.lead_max + item.freight_weeks for item in phase.items if not item.is_milestone),
            default=0,
        )
        phase.end_week = phase.start_week + max_lead


def generate_excel(schedule: Schedule, output_path: Path) -> None:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    _compute_schedule(schedule.phases)

    total_weeks = max((p.end_week for p in schedule.phases), default=12) + 2
    total_weeks = max(total_weeks, 12)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schedule"

    # ── Styles ────────────────────────────────────────────────────────────────
    # Aptos is the default Microsoft 365 font (2023+); Excel substitutes Arial on older installs.
    def F(**kw) -> Font:
        return Font(name="Aptos", **kw)

    PHASE_FONT  = F(bold=True, color="FFFFFF", size=11)
    PHASE_FILL  = PatternFill("solid", fgColor="1F4E79")
    PHASE_BAR   = PatternFill("solid", fgColor="2E75B6")
    HDR_FONT    = F(bold=True, size=9, color="FFFFFF")
    HDR_FILL    = PatternFill("solid", fgColor="2E75B6")
    ITEM_FONT   = F(size=10)
    MS_FONT     = F(bold=True, size=10, color="833C00")
    MS_BAR      = PatternFill("solid", fgColor="F4B942")
    # Two alternating bar shades so adjacent items are visually distinct
    BAR_FILLS     = [
        PatternFill("solid", fgColor="9DC3E6"),  # even rows: light blue
        PatternFill("solid", fgColor="5F9DD1"),  # odd rows:  medium blue
    ]
    # Sea freight band: soft green — reads as "in transit / logistics"
    FREIGHT_FILLS = [
        PatternFill("solid", fgColor="A9D18E"),  # even rows: light green
        PatternFill("solid", fgColor="70AD47"),  # odd rows:  medium green
    ]
    ALT_FILL      = PatternFill("solid", fgColor="EBF3FB")
    CENTER      = Alignment(horizontal="center", vertical="center", wrap_text=True)
    INDENT1     = Alignment(horizontal="left", vertical="center", indent=1)
    INDENT2     = Alignment(horizontal="left", vertical="center", indent=2)

    FIXED = 5   # Name | Lead Time | Origin | Start Wk | End Wk
    WK1   = FIXED + 1

    # ── Row 1: project title ─────────────────────────────────────────────────
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=FIXED + total_weeks)
    tc = ws.cell(row=1, column=1, value=schedule.project_name)
    tc.font = F(bold=True, size=13, color="1F4E79")
    tc.alignment = INDENT1
    ws.row_dimensions[1].height = 24

    # ── Row 2: column headers ─────────────────────────────────────────────────
    for ci, h in enumerate(["Item", "Lead Time", "Origin", "Start\nWk", "End\nWk"], 1):
        c = ws.cell(row=2, column=ci, value=h)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = CENTER

    for w in range(1, total_weeks + 1):
        wdate = schedule.start_date + timedelta(weeks=w - 1)
        c = ws.cell(row=2, column=WK1 + w - 1, value=f"W{w}\n{wdate.strftime('%d %b')}")
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = CENTER
    ws.row_dimensions[2].height = 40  # taller to show two-line date clearly

    # ── Data rows ─────────────────────────────────────────────────────────────
    row = 3
    for phase in schedule.phases:
        # Phase header
        for ci in range(1, FIXED + total_weeks + 1):
            ws.cell(row=row, column=ci).fill = PHASE_FILL
        ws.cell(row=row, column=1, value=phase.name).font = PHASE_FONT
        ws.cell(row=row, column=1).alignment = INDENT1
        if phase.start_week < phase.end_week:
            for ci in range(WK1 + phase.start_week, min(WK1 + phase.end_week, WK1 + total_weeks)):
                ws.cell(row=row, column=ci).fill = PHASE_BAR
        ws.row_dimensions[row].height = 18
        row += 1

        for j, item in enumerate(phase.items):
            bg = ALT_FILL if j % 2 == 0 else None
            bar_fill = BAR_FILLS[j % 2]

            if item.is_milestone:
                c = ws.cell(row=row, column=1, value=f"◆  {item.name}")
                c.font = MS_FONT
                c.alignment = INDENT2
                # Milestone falls at last week of its phase
                ms_week = (phase.end_week - 1) if phase.end_week > phase.start_week else phase.start_week
                ms_col = min(WK1 + ms_week, WK1 + total_weeks - 1)
                mc = ws.cell(row=row, column=ms_col)
                mc.value = "◆"
                mc.fill = MS_BAR
                mc.alignment = CENTER
                mc.font = F(bold=True, color="833C00")
            else:
                c = ws.cell(row=row, column=1, value=item.name)
                c.font = ITEM_FONT
                c.alignment = INDENT2

                lt = (f"{item.lead_max} wks" if item.lead_min == item.lead_max
                      else f"{item.lead_min}–{item.lead_max} wks") if item.lead_max else "–"
                ws.cell(row=row, column=2, value=lt).alignment = CENTER
                ws.cell(row=row, column=3, value=item.origin or "").alignment = CENTER
                ws.cell(row=row, column=4, value=phase.start_week + 1).alignment = CENTER
                # End Wk = delivery week (production + sea freight)
                ws.cell(row=row, column=5,
                        value=phase.start_week + item.lead_max + item.freight_weeks).alignment = CENTER

                if item.lead_max > 0:
                    for ci in range(
                        WK1 + phase.start_week,
                        min(WK1 + phase.start_week + item.lead_max, WK1 + total_weeks),
                    ):
                        ws.cell(row=row, column=ci).fill = bar_fill

                if item.freight_weeks > 0:
                    freight_start = WK1 + phase.start_week + item.lead_max
                    for ci in range(
                        freight_start,
                        min(freight_start + item.freight_weeks, WK1 + total_weeks),
                    ):
                        ws.cell(row=row, column=ci).fill = FREIGHT_FILLS[j % 2]

            if bg:
                for ci in range(1, FIXED + 1):
                    cell = ws.cell(row=row, column=ci)
                    if cell.fill.fgColor.rgb in ("00000000", "FFFFFFFF"):
                        cell.fill = bg

            ws.row_dimensions[row].height = 16
            row += 1

        # spacer
        ws.row_dimensions[row].height = 5
        row += 1

    # ── Column widths ─────────────────────────────────────────────────────────
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 7
    ws.column_dimensions["E"].width = 7
    for w in range(1, total_weeks + 1):
        ws.column_dimensions[get_column_letter(WK1 + w - 1)].width = 8.5  # wide enough for "01 Aug"

    ws.freeze_panes = ws.cell(row=3, column=WK1)

    wb.save(output_path)
