import csv
import json
import os
import re


def extract_book_number(filename):
    """
    Extract book number from filename like 'book_01.json' -> '1'
    """
    match = re.search(r'book_(\d+)\.json', filename)
    if match:
        return int(match.group(1))
    return None

def extract_headers_from_json(json_file_path, book_number):
    """
    Extract page numbers and headers from a JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file
        book_number (int): Book number
    
    Returns:
        list: List of dictionaries with book, page, and header data
    """
    try:
        # Read the JSON file
        with open(json_file_path, encoding='utf-8') as file:
            data = json.load(file)

        # Extract page and header data
        extracted_data = []

        # Check if data is a list or a single object
        if isinstance(data, list):
            # If it's a list of objects
            for item in data:
                if isinstance(item, dict) and 'page' in item and 'header' in item:
                    extracted_data.append({
                        'book': book_number,
                        'page': item['page'],
                        'header': item['header']
                    })
        elif isinstance(data, dict):
            # If it's a single object or has a different structure
            # Look for nested objects that might contain page and header
            def extract_from_dict(obj, result):
                if isinstance(obj, dict):
                    if 'page' in obj and 'header' in obj:
                        result.append({
                            'book': book_number,
                            'page': obj['page'],
                            'header': obj['header']
                        })
                    else:
                        # Recursively search nested dictionaries
                        for value in obj.values():
                            extract_from_dict(value, result)
                elif isinstance(obj, list):
                    # Recursively search lists
                    for item in obj:
                        extract_from_dict(item, result)

            extract_from_dict(data, extracted_data)

        return extracted_data

    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return []

def extract_all_headers_from_books_folder(books_folder, csv_file_path):
    """
    Extract headers from all JSON files in the books folder and save to CSV.
    
    Args:
        books_folder (str): Path to the books folder
        csv_file_path (str): Path to the output CSV file
    """
    all_data = []

    # Get all JSON files in the books folder
    try:
        files = [f for f in os.listdir(books_folder) if f.endswith('.json')]
        files.sort()  # Sort files to process in order

        for filename in files:
            book_number = extract_book_number(filename)
            if book_number is None:
                print(f"Warning: Could not extract book number from {filename}")
                continue

            json_file_path = os.path.join(books_folder, filename)
            print(f"Processing {filename} (Book {book_number})...")

            extracted_data = extract_headers_from_json(json_file_path, book_number)
            all_data.extend(extracted_data)

            print(f"  Extracted {len(extracted_data)} entries")

        # Sort by book number, then by page number
        all_data.sort(key=lambda x: (x['book'], x['page']))

        # Write to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['book', 'page', 'header']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header row
            writer.writeheader()

            # Write data rows
            for row in all_data:
                writer.writerow(row)

        print(f"\nSuccessfully extracted {len(all_data)} total entries to {csv_file_path}")
        if all_data:
            print(f"Book range: {all_data[0]['book']} to {all_data[-1]['book']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Extract headers from all books in the books folder
    books_folder = "books"
    csv_file = "all_books_headers.csv"

    extract_all_headers_from_books_folder(books_folder, csv_file)
