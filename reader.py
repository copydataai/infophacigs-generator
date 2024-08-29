import json
import requests
import os
from urllib.parse import urlparse, unquote
import re

def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_pdf_link(url):
    # Check if the URL ends with .pdf
    if url.lower().endswith('.pdf'):
        return True

    # If not, try to check the Content-Type header
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        content_type = response.headers.get('Content-Type', '').lower()
        return 'application/pdf' in content_type
    except requests.RequestException:
        return False

def sanitize_filename(filename):
    # Remove invalid characters from the filename
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_pdf(url, download_folder):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Try to get the filename from the Content-Disposition header
        filename = ""
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            filename = re.findall("filename=(.+)", content_disposition)
            if filename:
                filename = filename[0].strip('"')
            else:
                filename = None

        # If filename not in header, use the last part of the URL
        if not filename:
            filename = unquote(os.path.basename(urlparse(url).path))

        # If still no filename, use a generic name
        if not filename or not filename.lower().endswith('.pdf'):
            filename = 'downloaded_file.pdf'

        filename = sanitize_filename(filename)
        filepath = os.path.join(download_folder, filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Successfully downloaded: {filename}")
        return filepath
    except requests.RequestException as e:
        print(f"Failed to download from {url}. Error: {str(e)}")
        return None

def process_links(json_file, download_folder):
    data = read_json(json_file)

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for item in data:
        url = item['link']
        if is_pdf_link(url):
            filepath = download_pdf(url, download_folder)
            if filepath:
                item['local_file'] = filepath
        else:
            print(f"Not a PDF link: {url}")

    # Save updated JSON with local file paths
    with open('updated_' + json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    json_file = "search_results.json"  # Replace with your JSON file name
    download_folder = "downloaded_pdfs"
    process_links(json_file, download_folder)
    print("Processing complete. Check 'updated_search_results.json' for results.")
