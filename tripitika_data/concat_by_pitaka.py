import json
import os


def parse_book_ranges(range_string: str) -> list[tuple[int, int]]:
    """
    Parse a string like "1-5, 6-7, 8-20" into a list of tuples.
    
    Args:
        range_string (str): String containing book ranges
        
    Returns:
        List[Tuple[int, int]]: List of (start, end) tuples
        
    Example:
        "1-5, 6-7, 8-20" -> [(1, 5), (6, 7), (8, 20)]
    """
    ranges = []

    # Split by comma and clean up whitespace
    parts = [part.strip() for part in range_string.split(',')]

    for part in parts:
        if '-' in part:
            # Handle range like "1-5"
            start, end = part.split('-')
            try:
                start_num = int(start.strip())
                end_num = int(end.strip())
                ranges.append((start_num, end_num))
            except ValueError:
                print(f"Warning: Invalid range format '{part}', skipping...")
        else:
            # Handle single number like "5"
            try:
                num = int(part)
                ranges.append((num, num))
            except ValueError:
                print(f"Warning: Invalid number format '{part}', skipping...")

    return ranges

def get_available_books() -> list[int]:
    """
    Get list of available book numbers from the books folder.
    
    Returns:
        List[int]: List of available book numbers
    """
    available_books = []

    if not os.path.exists('books'):
        print("Error: 'books' folder not found!")
        return available_books

    for filename in os.listdir('books'):
        if filename.startswith('book_') and filename.endswith('.json'):
            try:
                book_num = int(filename[5:-5])  # Extract number from "book_XX.json"
                available_books.append(book_num)
            except ValueError:
                continue

    return sorted(available_books)

def load_book_data(book_num: int) -> list[dict]:
    """
    Load data from a specific book file.
    
    Args:
        book_num (int): Book number to load
        
    Returns:
        List[dict]: Book data as list of dictionaries
    """
    filename = f"books/book_{book_num:02d}.json"

    if not os.path.exists(filename):
        print(f"Warning: Book file '{filename}' not found, skipping...")
        return []

    try:
        with open(filename, encoding='utf-8') as file:
            data = json.load(file)

        if isinstance(data, list):
            return data
        else:
            print(f"Warning: Book {book_num} has unexpected format, skipping...")
            return []

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in book {book_num}: {e}")
        return []
    except Exception as e:
        print(f"Error loading book {book_num}: {e}")
        return []

def concatenate_books(book_ranges: list[tuple[int, int]]) -> list[list[dict]]:
    """
    Concatenate books according to specified ranges.
    
    Args:
        book_ranges (List[Tuple[int, int]]): List of (start, end) book ranges
        
    Returns:
        List[List[dict]]: List of concatenated book data for each range
    """
    available_books = get_available_books()

    if not available_books:
        print("No book files found in 'books' folder!")
        return []

    print(f"Available books: {available_books}")

    concatenated_data = []

    for start_book, end_book in book_ranges:
        print(f"\nProcessing range {start_book}-{end_book}...")

        range_data = []
        missing_books = []

        for book_num in range(start_book, end_book + 1):
            if book_num in available_books:
                book_data = load_book_data(book_num)
                if book_data:
                    range_data.extend(book_data)
                    print(f"  Added book {book_num} ({len(book_data)} pages)")
                else:
                    missing_books.append(book_num)
            else:
                missing_books.append(book_num)

        if missing_books:
            print(f"  Warning: Missing books {missing_books}")

        if range_data:
            concatenated_data.append(range_data)
            print(f"  Total pages in range {start_book}-{end_book}: {len(range_data)}")
        else:
            print(f"  No data found for range {start_book}-{end_book}")

    return concatenated_data

def save_concatenated_data(concatenated_data: list[list[dict]], output_prefix: str = "concatenated"):
    """
    Save concatenated data to JSON files.
    
    Args:
        concatenated_data (List[List[dict]]): List of concatenated book data
        output_prefix (str): Prefix for output filenames
    """
    for i, data in enumerate(concatenated_data):
        if not data:
            continue

        # Generate filename based on the book range
        start_book = data[0]['book'] if data else 0
        end_book = data[-1]['book'] if data else 0

        filename = f"{output_prefix}_books_{start_book:02d}-{end_book:02d}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            print(f"Saved: {filename} ({len(data)} pages)")

        except Exception as e:
            print(f"Error saving {filename}: {e}")

def main():
    """
    Main function to run the book concatenation script.
    """
    print("Book Concatenation Script")
    print("=" * 50)

    # Get available books
    available_books = get_available_books()

    if not available_books:
        print("No book files found in 'books' folder!")
        return

    print(f"Found {len(available_books)} book files: {available_books}")

    # Predefined book ranges - modify these as needed
    user_input = "1-8, 9-33, 34-45"
    print(f"\nUsing predefined ranges: {user_input}")

    try:
        # Parse the user input
        book_ranges = parse_book_ranges(user_input)

        if not book_ranges:
            print("No valid book ranges found.")
            return

        print(f"Parsed ranges: {book_ranges}")

        # Validate ranges against available books
        valid_ranges = []
        for start, end in book_ranges:
            if start > end:
                print(f"Warning: Invalid range {start}-{end} (start > end), skipping...")
                continue

            # Check if any books in the range exist
            range_books = [b for b in range(start, end + 1) if b in available_books]
            if not range_books:
                print(f"Warning: No books found in range {start}-{end}, skipping...")
                continue

            valid_ranges.append((start, end))

        if not valid_ranges:
            print("No valid book ranges found.")
            return

        # Concatenate the books
        concatenated_data = concatenate_books(valid_ranges)

        if concatenated_data:
            # Save the concatenated data
            save_concatenated_data(concatenated_data)
            print(f"\nSuccessfully created {len(concatenated_data)} concatenated files!")
        else:
            print("No data was concatenated.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
