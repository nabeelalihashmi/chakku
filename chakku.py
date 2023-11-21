import os
import sys
import json
import requests
import tempfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from csscompressor import compress as minify_css
from jsmin import jsmin

def download_file(url, local_path):
    response = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(response.content)

def minify_and_bundle_files(file_paths, output_path, minify_function):
    with open(output_path, 'w') as output_file:
        for file_path in file_paths:
            with open(file_path, 'r') as input_file:
                content = input_file.read()
                minified_content = minify_function(content)
                output_file.write(minified_content + '\n')

def process_config_entry(entry):
    files = entry.get("files", [])
    file_type = entry.get("type", "")
    output_path = entry.get("output", "")

    if not files or not file_type or not output_path:
        print("Error: Invalid configuration entry:", entry)
        return

    processed_files = []

    for file_path in files:
        if file_path.startswith(('http://', 'https://')):
            # Download online file to system temp dir
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as temp_file:
                download_file(file_path, temp_file.name)
                processed_files.append(temp_file.name)
        else:
            # Local file, use path with "./"
            processed_files.append('./' + file_path)

    # Minify and bundle files
    if file_type == "css":
        minify_and_bundle_files(processed_files, output_path, minify_css)
    elif file_type == "js":
        minify_and_bundle_files(processed_files, output_path, jsmin)
    else:
        print("Error: Unsupported file type:", file_type)
        return

    print(f'{file_type.upper()} files bundled and minified:', processed_files)

def process_config(config):
    for entry in config:
        process_config_entry(entry)

def print_ascii_header():
    ascii_header = """         
    Chakku - Config Based CSS and JS Bundler
    Website: aliveforms.com/opensource#chakku
    """
    print(ascii_header)

def main(config_file):
    print_ascii_header()

    with open(config_file, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {config_file}: {e}")
            sys.exit(1)

    process_config(config)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python chakku.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    main(config_file)
