# Tripitaka Data Extractor

This Python script extracts structured data from Tripitaka HTML files. It parses each page (separated by `<hr>` tags) and extracts:

- **Book number** - Extracted from the footer in Thai numerals
- **Page number** - Extracted from the footer in Thai numerals  
- **Content** - Clean text content with all HTML tags removed
- **Footnotes** - Footnotes and annotations from the page

## Features

- **Batch Processing**: Process entire folders of HTML files at once
- Converts Thai numerals (๐-๙) to Arabic numerals (0-9)
- Removes all HTML tags and formatting from content
- Handles multiple file encodings (UTF-8, TIS-620)
- Outputs structured JSON data
- Provides detailed summary of extracted data
- Error handling with individual file processing

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Batch Processing

Process all HTML files in a folder:

```bash
python extract_tripitaka.py input_folder output_folder
```

### Advanced Options

```bash
python extract_tripitaka.py input_folder output_folder --encoding utf-8 --pattern "*.htm*"
```

### Command Line Arguments

- `input_folder`: Source folder containing HTML files
- `output_folder`: Destination folder for JSON files
- `--encoding`: File encoding (default: utf-8)
- `--pattern`: File pattern to match (default: *.htm*)

### Examples

```bash
# Process all HTML files with default settings
python extract_tripitaka.py input/ output/

# Process only .htm files with specific encoding
python extract_tripitaka.py input/ output/ --encoding tis-620 --pattern "*.htm"

# Process with UTF-8 encoding (explicit)
python extract_tripitaka.py input/ output/ --encoding utf-8
```

## Output Format

Each JSON file contains an array of page objects with the following structure:

```json
[
  {
    "book": 1,
    "page": 1,
    "page_index": 0,
    "header": "พระไตรปิฎกเล่มที่ ๐๑-๑ สุตตันตปิฎกที่ ๐๑ ทีฆนิกาย สีลขันธวรรค",
    "contents": [
      "พระสุตตันตปิฎก ทีฆนิกาย สีลขันธวรรค [๑.พรหมชาลสูตร] เรื่องสุปปิยปริพาชกกับพรหมทัตมาณพ...",
      "ขอนอบน้อมพระผู้มีพระภาคอรหันตสัมมาสัมพุทธเจ้าพระองค์นั้น..."
    ],
    "footnotes": [
      "เชิงอรรถ : ๑ คำว่า ข้าพเจ้า ในตอนเริ่มต้นของพระสูตรนี้และพระสูตรอื่น ๆ ในเล่มนี้ หมายถึงพระอานนท์..."
    ]
  }
]
```

## Batch Processing Features

- **Automatic Folder Creation**: Creates output folder if it doesn't exist
- **Pattern Matching**: Supports glob patterns to filter files
- **Progress Tracking**: Shows processing status for each file
- **Error Handling**: Continues processing even if individual files fail
- **Summary Report**: Provides detailed statistics after processing

## Book Concatenation

After extracting data from individual files, you can concatenate all pages by book number using the `concat_by_book.py` script:

```bash
python concat_by_book.py output_folder books_folder
```

This creates one JSON file per book (e.g., `book_01.json`, `book_02.json`) with all pages sorted by page number.

### Concatenation Features

- **Book Organization**: Creates one file per book
- **Page Sorting**: Sorts pages by page number within each book
- **Duplicate Detection**: Reports errors for duplicate book/page combinations
- **Data Validation**: Ignores pages with book number 0
- **Clean Output**: Removes `page_index` field from final output
- **Comprehensive Reporting**: Generates detailed summary statistics

### Concatenation Output

Each book file contains an array of pages without the `page_index` field:

```json
[
  {
    "book": 1,
    "page": 1,
    "header": "พระไตรปิฎกเล่มที่ ๐๑-๑ สุตตันตปิฎกที่ ๐๑ ทีฆนิกาย สีลขันธวรรค",
    "contents": ["..."],
    "footnotes": ["..."]
  }
]
```

## Advanced Book Concatenation

For more flexible book concatenation, you can use the `concat_by_pitaka.py` script to combine specific book ranges into custom groupings:

### Usage

```bash
python concat_by_pitaka.py
```

The script uses predefined book ranges that you can modify in the source code. By default, it creates three concatenated files:

- **Books 1-8**: Vinaya Pitaka (Discipline Basket)
- **Books 9-33**: Sutta Pitaka (Discourse Basket) 
- **Books 34-45**: Abhidhamma Pitaka (Higher Teaching Basket)

### Customizing Ranges

To change the book ranges, modify the `user_input` variable in `concat_by_pitaka.py`:

```python
# Predefined book ranges - modify these as needed
user_input = "1-8, 9-33, 34-45"
```

### Range Format

- **Single books**: `"1, 3, 5"`
- **Book ranges**: `"1-5, 6-10"`
- **Mixed format**: `"1-3, 5, 7-9"`

### Output Files

The script generates files with descriptive names:

- `concatenated_books_01-08.json` - Books 1-8 combined
- `concatenated_books_09-33.json` - Books 9-33 combined  
- `concatenated_books_34-45.json` - Books 34-45 combined

### Features

- **Flexible Range Specification**: Support for single books, ranges, and mixed formats
- **Automatic Validation**: Checks for missing books and provides warnings
- **Progress Reporting**: Shows detailed processing information
- **Error Handling**: Gracefully handles missing or corrupted files
- **Preserves Structure**: Maintains the same JSON format as input files

## Header Extraction

Extract page headers from book JSON files using the `extract_headers.py` script:

### Usage

```bash
python extract_headers.py
```

This script extracts page numbers and headers from `books/book_01.json` and creates a CSV file with two columns: `page` and `header`.

### Output

Creates `book_01_headers.csv` with the following format:

```csv
page,header
1,พระไตรปิฎกเล่มที่ ๐๑-๑ วินัยปิฎกที่ ๐๑ มหาวิภังค์ ภาค ๑
2,พระวินัยปิฎก มหาวิภังค์ เวรัญชกัณฑ์
3,พระวินัยปิฎก มหาวิภังค์ เวรัญชกัณฑ์
...
```

### Features

- **Automatic Processing**: Extracts all headers from the specified book file
- **CSV Output**: Creates a structured CSV file for easy analysis
- **Page Sorting**: Entries are sorted by page number
- **Error Handling**: Gracefully handles missing or corrupted files
- **UTF-8 Support**: Properly handles Thai text encoding

## Error Handling

The script handles various error conditions gracefully:

- **File Encoding Issues**: Attempts multiple encodings automatically
- **Malformed HTML**: Skips problematic files and continues processing
- **Missing Files**: Reports missing files without stopping
- **Permission Errors**: Logs permission issues and continues
- **JSON Writing Errors**: Reports write failures for individual files

## Requirements

- Python 3.6+
- BeautifulSoup4
- argparse (built-in)
- json (built-in)
- os (built-in)
- glob (built-in)
- re (built-in)

## File Structure

```
tripitaka-offline/
├── extract_tripitaka.py      # Main extraction script
├── concat_by_book.py         # Book concatenation script
├── concat_by_pitaka.py           # Advanced book concatenation script
├── extract_headers.py        # Header extraction script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── input/                   # Source HTML files
├── output/                  # Individual JSON files
├── books/                   # Concatenated book files
├── concatenated_books_*.json # Advanced concatenation output
└── book_*_headers.csv       # Header extraction output
```

## Processing Workflow

1. **Extract Data**: Run `extract_tripitaka.py` to process HTML files
2. **Concatenate Books**: Run `concat_by_book.py` to organize by book
3. **Advanced Concatenation**: Run `concat_by_pitaka.py` to create custom book groupings
4. **Extract Headers**: Run `extract_headers.py` to extract page headers for analysis
5. **Review Results**: Check summary files for processing statistics
6. **Use Data**: Access organized book files for analysis or display

## Notes

- The script automatically converts Thai numerals to Arabic numerals
- All HTML formatting is removed from content
- Footnotes are preserved in their original format
- Page headers are extracted from the document structure
- The script supports both UTF-8 and TIS-620 encodings 