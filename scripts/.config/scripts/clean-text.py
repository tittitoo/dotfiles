#!/usr/bin/env -S uv run --script

# Helper scripts to clean text
# Meant to be passed from echo command
# Use in FZF_DEFAULT_OPTS

import sys


def extract_filename(text):
    "Extract folder name from a path"
    text = text.strip()
    if text.endswith("/"):
        text = text[:-1]
    return text.split("/")[-1]


def main():
    if len(sys.argv) > 1:
        # Input from command line
        input_string = " ".join(sys.argv[1:])
    else:
        input_string = sys.stdin.read().strip()
    filename = extract_filename(input_string)
    print(filename, end="")


if __name__ == "__main__":
    main()
