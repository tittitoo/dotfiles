#!/usr/bin/env -S uv run --script

# Helper scripts to clean text for outlook folder
# Meant to be passed from echo command
# Use in FZF_DEFAULT_OPTS
# E.g. J12662 GOE - SAKARYA PHASE-2A FPU - COM changed to
# J12662 COM GOE SAKARYA PHASE-2A FPU
# --bind "ctrl-r:execute(echo {} | clean-text-outlook | pbcopy)"

# Sample data
# 2026/J12795 HOS - P91 FPSO - ENT/
# 2026/J12792 HOS - P91 FPSO - POB/
# 2026/J12806 HOS - P91 FPSO - COM/
# 2026/J12791 HOS - P91 FPSO - AERO/
# 2026/J12794 HOS - P91 FPSO - CCTV/
# 2026/J12793 HOS - P91 FPSO - PAGA/
# 2025/J12766 HOS - SEAP II FPSO - COM/
# 2026/J12801 HOS - P91 FPSO - DC POWER/

# Requirement to transform
# J12801 DC POWER HOS P91 FPSO
# J12794 CCTV HOS P91 FPSO

import sys
import re


def extract_filename(text):
    "Extract folder/filename name from a path"
    text = text.strip()
    if text.endswith("/"):
        text = text[:-1]
    text = text.split("/")[-1]  # Get folder name
    pattern = r"(\s+[-–—])|([-–—]+\s+)"
    text = re.split(pattern, text)
    text = [word for word in text if word is not None]
    text = [word for word in text if word.strip() not in ("-", "–", "—")]
    text = [word.strip() for word in text]
    if len(text) < 2:
        return " ".join(text[:])
    last_word = text.pop()
    first_phrase = text[0].split()
    text = " ".join([first_phrase[0], last_word] + first_phrase[1:] + text[1:])
    return text


def main():
    if len(sys.argv) > 1:
        # Input from the command line
        input_string = " ".join(sys.argv[1:])
    else:
        input_string = sys.stdin.read().strip()

    filename = extract_filename(input_string)
    print(filename, end="")


if __name__ == "__main__":
    main()
