#!/usr/bin/env python3

"""
Streaming URL/User Log Parser.

Supported input formats:

    URL:USER
    URL:USER:SECRET

The parser intentionally extracts only URL and USER.
The third/secret field is ignored.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse


def looks_like_url(value: str) -> bool:
    value = value.strip()

    if not value:
        return False

    try:
        test_value = value if "://" in value else "https://" + value
        parsed = urlparse(test_value)

        return bool(parsed.netloc) and "." in parsed.netloc

    except Exception:
        return False


def split_record(line: str):
    """
    Parse:

        URL:USER
        URL:USER:SECRET

    Returns:

        (url, user)

    The third field is deliberately ignored.
    """

    line = line.strip()

    if not line:
        return None

    parts = line.split(":", 2)

    if len(parts) == 3:
        url, user, _secret = parts

        if looks_like_url(url):
            return url, user

    elif len(parts) == 2:
        url, user = parts

        if looks_like_url(url):
            return url, user

    return None


def detect_format(path: Path, sample_lines: int = 100) -> str:
    """
    Inspect the first sample_lines records.

    Returns:

        url:user
        url:user:secret
        unknown
    """

    url_user = 0
    url_user_secret = 0

    with path.open(
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as source:

        for _ in range(sample_lines):

            line = source.readline()

            if not line:
                break

            parts = line.strip().split(":", 2)

            if len(parts) == 3 and looks_like_url(parts[0]):
                url_user_secret += 1

            elif len(parts) == 2 and looks_like_url(parts[0]):
                url_user += 1

    if url_user_secret:
        return "url:user:secret"

    if url_user:
        return "url:user"

    return "unknown"


def extract(line: str, field: str):

    record = split_record(line)

    if record is None:
        return []

    url, user = record

    if field == "url":
        return [url]

    if field == "user":
        return [user]

    if field == "both":
        return [url, user]

    return []


def process_file(path: Path, output, field: str) -> int:

    count = 0

    with path.open(
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as source:

        # Streaming: only one line is held in memory.
        for line in source:

            values = extract(line, field)

            for value in values:

                if value:
                    output.write(value + "\n")
                    count += 1

    return count


def iter_files(
    source_file: str | None,
    source_folder: str | None,
    recursive: bool,
):

    if source_file:
        yield Path(source_file)
        return

    folder = Path(source_folder)

    if recursive:
        iterator = folder.rglob("*.txt")
    else:
        iterator = folder.glob("*.txt")

    for path in iterator:

        if path.is_file():
            yield path


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Streaming parser for URL:user log records."
        )
    )

    source = parser.add_mutually_exclusive_group(
        required=True
    )

    source.add_argument(
        "--file",
        help="Process a single TXT file",
    )

    source.add_argument(
        "--folder",
        help="Process TXT files inside a directory",
    )

    parser.add_argument(
        "--field",
        choices=[
            "url",
            "user",
            "both",
        ],
        required=True,
        help="Field to extract",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively",
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically detect the input record format",
    )

    parser.add_argument(
        "--output",
        help="Specify output TXT file",
    )

    args = parser.parse_args()

    input_files = list(
        iter_files(
            args.file,
            args.folder,
            args.recursive,
        )
    )

    if not input_files:
        raise SystemExit(
            "No TXT files found."
        )

    # Determine output filename.

    if args.output:

        output_path = Path(args.output)

    elif args.file:

        input_path = Path(args.file)

        output_path = input_path.with_name(
            input_path.stem + "_filtered.txt"
        )

    else:

        output_path = (
            Path(args.folder)
            / f"all_{args.field}_filtered.txt"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Don't process our own output file.

    output_resolved = output_path.resolve()

    input_files = [
        path
        for path in input_files
        if path.resolve() != output_resolved
    ]

    total = 0

    with output_path.open(
        "w",
        encoding="utf-8",
        buffering=1024 * 1024,
    ) as output:

        for path in input_files:

            try:

                if args.auto:

                    detected = detect_format(path)

                else:

                    detected = None

                count = process_file(
                    path,
                    output,
                    args.field,
                )

                total += count

                if detected:

                    print(
                        f"[+] {path} | "
                        f"detected={detected} | "
                        f"extracted={count:,}"
                    )

                else:

                    print(
                        f"[+] {path} | "
                        f"extracted={count:,}"
                    )

            except OSError as error:

                print(
                    f"[!] {path}: {error}"
                )

    print()
    print(
        f"Files processed : {len(input_files):,}"
    )

    print(
        f"Values written  : {total:,}"
    )

    print(
        f"Output          : {output_path}"
    )


if __name__ == "__main__":
    main()
