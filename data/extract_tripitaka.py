#!/usr/bin/env python3
"""
Tripitaka Data Extractor

This script extracts structured data from Tripitaka HTML files.
It parses each page (separated by <hr> tags) and extracts:
- Book number
- Page number  
- Content (as clean text)
- Footnotes

The page information is extracted from the footer which contains Thai numerals.
"""

import argparse
import glob
import json
import os
import re

from bs4 import BeautifulSoup

# Thai numeral to Arabic numeral mapping
THAI_TO_ARABIC = {
    '๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4',
    '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'
}

# {ที่มา : โปรแกรมพระไตรปิฎกภาษาไทย ฉบับมหาจุฬาลงกรณราชวิทยาลัย เล่ม : ๑ หน้า:๖ }
footer_pattern = r'\{ที่มา\s*:\s*โปรแกรมพระไตรปิฎกภาษาไทย\s*ฉบับมหาจุฬาลงกรณราชวิทยาลัย\s*เล่ม\s*:\s*([๐-๙]+)\s*หน้า\s*:\s*([๐-๙]+)\s*\}'

def thai_to_arabic(thai_num: str) -> int:
    """Convert Thai numerals to Arabic numerals."""
    arabic_str = ''
    for char in thai_num:
        if char in THAI_TO_ARABIC:
            arabic_str += THAI_TO_ARABIC[char]
        else:
            arabic_str += char
    return int(arabic_str) if arabic_str.isdigit() else 0

def clean_text(text: str) -> str:
    """Clean text by removing HTML tags and extra whitespace."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove extra newlines
    text = re.sub(r'[\r\n]+', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

def extract_footnotes(soup: BeautifulSoup) -> tuple[int, int, list[str]]:
    """Extract footnotes from the page."""
    book_number = 0
    page_number = 0
    footnotes = []

    # Look for footer elements, but avoid duplicates by using a set
    footer_elements = set()

    # Find all p elements with class="footer"
    p_footers = soup.find_all('p', class_='footer')
    for p in p_footers:
        footer_elements.add(p)

    # Find all span elements with class="footer" that are NOT inside p elements with class="footer"
    span_footers = soup.find_all('span', class_='footer')
    for span in span_footers:
        # Check if this span is inside a p with class="footer"
        parent_p = span.find_parent('p', class_='footer')
        if not parent_p:
            footer_elements.add(span)

    for element in footer_elements:
        text = clean_text(element.get_text())
        match = re.search(footer_pattern, text)

        if match:
            book_number = thai_to_arabic(match.group(1))
            page_number = thai_to_arabic(match.group(2))

        # Remove the page info footer part that's always at the end using strict regex
        text = re.sub(footer_pattern, '', text).strip()

        if text:
            footnotes.append(text)

    return book_number, page_number, footnotes


def extract_content(soup: BeautifulSoup) -> tuple[str, list[str], list[str]]:
    """Extract main content from the page, excluding footnotes and headers."""
    page_header = None
    content_parts = []
    footnotes = []

    # Find all paragraph tags
    paragraphs = soup.find_all('p')

    for p in paragraphs:
        # Skip if it's a subject or footer paragraph
        if p.get('class') and ('footer' in p.get('class') or 'subject' in p.get('class')):
            continue

        # Get text content, but exclude footer spans
        text_content = ""
        for content in p.contents:
            if hasattr(content, 'name') and content.name == 'span' and 'footer' in content.get('class', []):
                # Skip footer content
                continue
            elif hasattr(content, 'name'):
                # It's a tag, get its text content
                text_content += content.get_text()
            else:
                # It's a text node
                text_content += str(content)
        cleaned = clean_text(text_content)

        # Extract header/title (first line of first paragraph)
        if page_header is None:
            lines = p.get_text().split('\n')

            for line in lines:
                line = clean_text(line)
                if line == '':
                    continue
                page_header = line
                cleaned = cleaned.replace(page_header, '', 1).strip()
                break

        if cleaned and cleaned != '':
            # Check if 'เชิงอรรถ' appears in the text
            footnote_index = cleaned.find('เชิงอรรถ')
            if footnote_index != -1:
                # Split the text: part before 'เชิงอรรถ' goes to content, part after (including 'เชิงอรรถ') goes to footnotes
                content_part = cleaned[:footnote_index].strip()
                footnote_part = cleaned[footnote_index:].strip()

                if content_part:
                    content_parts.append(content_part)
                if footnote_part:
                    footnotes.append(footnote_part)
            else:
                # No 'เชิงอรรถ' found, add to content
                content_parts.append(cleaned)


    return page_header, content_parts, footnotes

def extract_page_data(html_content: str) -> list[dict]:
    """Extract structured data from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Split content by <hr> tags
    hr_tags = soup.find_all('hr')

    if not hr_tags:
        # If no <hr> tags, treat entire content as one page
        pages = [soup]
    else:
        # Split content into pages based on <hr> tags
        pages = []
        current_content = []

        for element in soup.find_all(['p', 'hr', 'span']):
            if element.name == 'hr':
                if current_content:
                    # Create a new soup object for this page
                    page_html = ''.join(str(tag) for tag in current_content)
                    page_soup = BeautifulSoup(page_html, 'html.parser')
                    pages.append(page_soup)
                    current_content = []
            else:
                current_content.append(element)

        # Add the last page if there's content
        if current_content:
            page_html = ''.join(str(tag) for tag in current_content)
            page_soup = BeautifulSoup(page_html, 'html.parser')
            pages.append(page_soup)

    extracted_data = []

    for i, page_soup in enumerate(pages):
        page_data = {
            'page_index': i + 1,
            'book': 0,
            'page': 0,
            'header': '',
            'contents': [],
            'footnotes': []
        }

        # Extract content
        page_data['header'], page_data['contents'], footnote1 = extract_content(page_soup)

        # Extract footnote
        page_data['book'], page_data['page'], footnote2 = extract_footnotes(page_soup)

        page_data['footnotes'] = footnote1 + footnote2

        extracted_data.append(page_data)

    return extracted_data

def process_file(input_file: str, output_file: str, encoding: str = 'utf-8') -> bool:
    """Process a single HTML file and extract data to JSON."""
    try:
        # Read input file
        try:
            with open(input_file, encoding=encoding) as f:
                html_content = f.read()
        except UnicodeDecodeError:
            # Try with windows-874 encoding (common for Thai files)
            try:
                with open(input_file, encoding='tis-620') as f:
                    html_content = f.read()
            except UnicodeDecodeError:
                print(f"Error: Could not read file {input_file} with encodings {encoding} or tis-620")
                return False

        # Extract data
        print(f"Processing {input_file}...")
        extracted_data = extract_page_data(html_content)

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"Extracted {len(extracted_data)} pages")
        print(f"Data saved to {output_file}")
        return True

    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Extract structured data from Tripitaka HTML files')
    parser.add_argument('input_folder', help='Input folder containing HTML files')
    parser.add_argument('output_folder', help='Output folder for JSON files')
    parser.add_argument('--encoding', default='utf-8', help='File encoding (default: utf-8)')
    parser.add_argument('--pattern', default='tpd*.htm', help='File pattern to match (default: tpd*.htm)')

    args = parser.parse_args()

    # Check if input folder exists
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist")
        return 1

    # Create output folder if it doesn't exist
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    # Find all HTML files in the input folder
    pattern = os.path.join(args.input_folder, args.pattern)
    html_files = glob.glob(pattern)

    if not html_files:
        print(f"No files found matching pattern '{args.pattern}' in folder '{args.input_folder}'")
        return 1

    print(f"Found {len(html_files)} files to process")

    # Process each file
    successful = 0
    failed = 0

    for input_file in html_files:
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(args.output_folder, f"{base_name}.json")

        if process_file(input_file, output_file, args.encoding):
            successful += 1
        else:
            failed += 1

    print("\nProcessing complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
