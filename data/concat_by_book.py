#!/usr/bin/env python3
"""
Tripitaka Book Concatenator

This script concatenates all JSON output files from the Tripitaka extractor
and organizes them by book number. It creates one JSON file per book,
ignoring any data with book number 0, and reports errors for duplicate
page and book combinations.
"""

import argparse
import glob
import json
import os
from collections import defaultdict


def load_json_file(file_path: str) -> list[dict]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return []

def validate_page_data(pages: list[dict]) -> tuple[bool, list[str]]:
    """Validate page data for duplicates and other issues."""
    errors = []
    seen_pages = set()

    for page in pages:
        book = page.get('book', 0)
        page_num = page.get('page', 0)

        # Skip pages with book number 0
        if book == 0:
            continue

        # Check for duplicate book/page combinations
        page_key = (book, page_num)
        if page_key in seen_pages:
            errors.append(f"Duplicate book {book}, page {page_num} found")
        else:
            seen_pages.add(page_key)

    return len(errors) == 0, errors

def organize_by_book(input_folder: str) -> tuple[dict[int, list[dict]], list[str]]:
    """Load all JSON files and organize pages by book number."""
    all_errors = []
    books_data = defaultdict(list)

    # Find all JSON files in the input folder
    pattern = os.path.join(input_folder, "*.json")
    json_files = glob.glob(pattern)

    if not json_files:
        all_errors.append(f"No JSON files found in {input_folder}")
        return dict(books_data), all_errors

    print(f"Found {len(json_files)} JSON files to process")

    # Process each JSON file
    for json_file in json_files:
        print(f"Processing {os.path.basename(json_file)}...")
        pages = load_json_file(json_file)

        if not pages:
            continue

        # Validate pages in this file
        is_valid, file_errors = validate_page_data(pages)
        all_errors.extend(file_errors)

        # Organize pages by book number
        for page in pages:
            book = page.get('book', 0)
            if book > 0:  # Only include pages with valid book numbers
                books_data[book].append(page)

    return dict(books_data), all_errors

def sort_pages_by_page_number(pages: list[dict]) -> list[dict]:
    """Sort pages by page number within each book."""
    return sorted(pages, key=lambda x: x.get('page', 0))

def save_book_files(books_data: dict[int, list[dict]], output_folder: str) -> list[str]:
    """Save each book's data to a separate JSON file."""
    errors = []

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for book_num, pages in books_data.items():
        if not pages:
            continue

        # Sort pages by page number
        sorted_pages = sort_pages_by_page_number(pages)

        # Remove page_index from each page
        cleaned_pages = []
        for page in sorted_pages:
            # Create a copy of the page without page_index
            cleaned_page = {k: v for k, v in page.items() if k != 'page_index'}
            cleaned_pages.append(cleaned_page)

        # Create output filename
        output_file = os.path.join(output_folder, f"book_{book_num:02d}.json")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_pages, f, ensure_ascii=False, indent=2)
            print(f"Saved book {book_num} with {len(cleaned_pages)} pages to {output_file}")
        except Exception as e:
            error_msg = f"Error saving book {book_num}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)

    return errors

def generate_summary(books_data: dict[int, list[dict]], errors: list[str]) -> str:
    """Generate a summary report."""
    summary = []
    summary.append("=" * 50)
    summary.append("TRIPITAKA BOOK CONCATENATION SUMMARY")
    summary.append("=" * 50)

    if books_data:
        summary.append(f"\nBooks processed: {len(books_data)}")
        total_pages = sum(len(pages) for pages in books_data.values())
        summary.append(f"Total pages: {total_pages}")

        summary.append("\nBook details:")
        for book_num in sorted(books_data.keys()):
            pages = books_data[book_num]
            summary.append(f"  Book {book_num:2d}: {len(pages):4d} pages")
    else:
        summary.append("\nNo books found!")

    if errors:
        summary.append(f"\nErrors found: {len(errors)}")
        for error in errors:
            summary.append(f"  - {error}")
    else:
        summary.append("\nNo errors found!")

    summary.append("=" * 50)
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description='Concatenate Tripitaka JSON files by book number')
    parser.add_argument('input_folder', help='Input folder containing JSON files')
    parser.add_argument('output_folder', help='Output folder for book files')
    parser.add_argument('--summary', action='store_true', help='Print detailed summary')

    args = parser.parse_args()

    # Check if input folder exists
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist")
        return 1

    print(f"Processing JSON files from: {args.input_folder}")
    print(f"Output folder: {args.output_folder}")

    # Organize data by book
    books_data, errors = organize_by_book(args.input_folder)

    # Save book files
    save_errors = save_book_files(books_data, args.output_folder)
    errors.extend(save_errors)

    # Generate and print summary
    summary = generate_summary(books_data, errors)
    print(summary)

    # Save summary to file
    summary_file = os.path.join(args.output_folder, "concatenation_summary.txt")
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"\nSummary saved to: {summary_file}")
    except Exception as e:
        print(f"Error saving summary: {str(e)}")

    # Return appropriate exit code
    if errors:
        print(f"\nWARNING: {len(errors)} errors found!")
        return 1
    else:
        print("\nSUCCESS: All books processed successfully!")
        return 0

if __name__ == "__main__":
    exit(main())
