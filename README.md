# PO File Translator for Django Projects

A Python script to translate PO (Portable Object) files generated in Django projects using the DeepL translation API.

## Features

- Translates untranslated strings in PO files
- Uses DeepL API for high-quality translations
- Command-line interface for easy integration into workflows
- Preserves PO file structure and metadata
- Skips already translated entries to save API calls
- Preserves formatted strings like `{variable}` and `%(variable)s` during translation

## Requirements

- Python 3.9+
- `polib`: For handling PO files
- `deepl`: Official DeepL Python library for translations
- DeepL API key (free or pro)

## Installation

### Option 1: Install from Source

1. Clone this repository or download the script:

```bash
git https://github.com/Marco-Meo/Translator_Django.git
cd Translator_Django
```

2. Install the package and its dependencies:

```bash
pip install -e .
```

This will install the package in development mode and create a command-line tool called `po-translator`.

### Option 2: Install Dependencies Only

If you prefer not to install the package, you can just install the required dependencies:

```bash
pip install polib deepl
```

3. Get a DeepL API key:
   - Sign up for a free account at [DeepL API](https://www.deepl.com/pro-api)
   - Copy your API key from the account dashboard

## Usage

### Basic Usage

If you installed the package using `pip install -e .`, you can use the command-line tool:

```bash
po-translator <po_file_path> <source_lang> <target_lang> --api-key <your_deepl_api_key>
```

Alternatively, you can run the script directly:

```bash
python po_translator.py <po_file_path> <source_lang> <target_lang> --api-key <your_deepl_api_key>
```

### Using Helper Scripts

For convenience, this repository includes helper scripts for both Windows and Unix-based systems:

#### Windows

```bash
translate.bat <po_file_path> <source_lang> <target_lang> [api_key]
```

Example:
```bash
translate.bat example.po en-us de YOUR_API_KEY
```

#### Linux/Mac

```bash
./translate.sh <po_file_path> <source_lang> <target_lang> [api_key]
```

Example:
```bash
./translate.sh example.po en es YOUR_API_KEY
```

Note: You may need to make the script executable first:
```bash
chmod +x translate.sh
```

### Example

```bash
python po_translator.py locale/es/LC_MESSAGES/django.po en es --api-key YOUR_DEEPL_API_KEY
```

### Using the Example PO File

This repository includes an example PO file (`example.po`) that you can use to test the script:

```bash
python po_translator.py example.po en es --api-key YOUR_DEEPL_API_KEY
```

This will translate the example strings from English to Spanish.

### Using Environment Variable

You can also set your DeepL API key as an environment variable:

```bash
# On Windows
set DEEPL_API_KEY=your_deepl_api_key

# On Linux/Mac
export DEEPL_API_KEY=your_deepl_api_key
```

Then run the script without the `--api-key` parameter:

```bash
python po_translator.py locale/es/LC_MESSAGES/django.po en-us es
```

## Language Codes

Use standard language codes for the source and target languages:

- English: `en-us`
- Spanish: `es`
- French: `fr`
- German: `de`
- Italian: `it`
- Dutch: `nl`
- Polish: `pl`
- Portuguese: `pt`
- Russian: `ru`
- Japanese: `ja`
- Chinese: `zh`

For a complete list of supported languages, refer to the [DeepL API documentation](https://www.deepl.com/docs-api/translating-text/).

## Limitations

- The script currently skips entries with plural forms, which require more complex handling
- DeepL API has usage limits depending on your subscription plan
- Some context-specific translations might need manual review

## Handling Formatted Strings

The translator automatically preserves formatted strings during translation. This is important for strings that contain placeholders that will be replaced with actual values at runtime.

### Supported Format Types

- Python brace format: `"Hello {name}, welcome to {place}!"`
- Python percent format: `"Hello %(name)s, your score is %(score)d!"`

These placeholders are identified and protected during the translation process, ensuring they remain unchanged in the translated text. This prevents issues that would occur if the placeholders were translated.

### Example

Original string:
```
"User {username} has {count} messages"
```

Translated to German (with placeholders preserved):
```
"Benutzer {username} hat {count} Nachrichten"
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Testing

The project includes a comprehensive test suite using pytest. The tests cover all major components of the script:

- DeepLTranslator class
- POFileTranslator class
- Command-line interface

### Installing Test Dependencies

To install the required testing dependencies:

```bash
pip install -r requirements.txt
```

Or install them directly:

```bash
pip install pytest pytest-mock
```

### Running Tests

To run the tests:

```bash
pytest
```

For more verbose output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_deepl_translator.py
```

### Test Coverage

The tests use mocking to avoid making actual API calls to DeepL, so you can run them without a valid API key.
