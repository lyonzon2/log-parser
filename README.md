# Streaming URL/User Log Parser

A lightweight Python utility for processing large TXT log files without
loading the entire files into RAM.

## Features

- Single-file processing
- Directory processing
- Recursive directory processing
- Streaming / low-memory operation
- Automatic format detection
- UTF-8 support
- Invalid-character tolerance
- No third-party dependencies
- Automatic output filenames
- Supports URL and user extraction

## Supported records

The parser understands records such as:

    https://example.com:alice@example.com

and:

    https://example.org:bob@example.org:SECRET

For records containing a third field, the third field is ignored.

The project intentionally does not extract or output passwords/secrets.

## Requirements

Python 3.9 or newer.

No external Python packages are required.

## Installation

Clone the repository:

    git clone https://github.com/YOUR_USERNAME/log-parser.git

Enter the directory:

    cd log-parser

## Usage

### Extract URLs

    python parser.py --file input.txt --field url

Output:

    input_filtered.txt

### Extract users

    python parser.py --file input.txt --field user

### Extract both

    python parser.py --file input.txt --field both

## Directory mode

Process every TXT file:

    python parser.py --folder ./logs --field user

## Recursive directory mode

Process TXT files in all subdirectories:

    python parser.py --folder ./logs --recursive --field user

## Automatic detection

Use:

    python parser.py --folder ./logs --recursive --auto --field user

The program examines a small sample of every file and reports whether the
records look like:

    URL:USER

or:

    URL:USER:SECRET

The secret field is not extracted.

## Custom output

    python parser.py \
        --folder ./logs \
        --recursive \
        --field user \
        --output users.txt

## Memory usage

The parser processes files line-by-line:

    for line in source:

It does not use:

    source.read()

or:

    source.readlines()

Therefore a very large file does not need to fit into RAM.

For example, a 20 GB TXT file is processed sequentially instead of loading
20 GB into memory.

## Example

Input:

    https://example.com:alice@example.com
    https://example.org:bob@example.org:placeholder
    https://example.net:charlie@example.net

Run:

    python parser.py --file sample.log --field user

Output:

    alice@example.com
    bob@example.org
    charlie@example.net

## Security

Use this software only on data you are authorized to process.

Do not commit credentials, API keys, authentication tokens, or other secrets
to GitHub.

The parser deliberately does not extract or output secret/password fields.

## License

MIT
