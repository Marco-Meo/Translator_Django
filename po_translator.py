#!/usr/bin/env python
"""
PO File Translator using DeepL API

This script translates PO (Portable Object) files generated in Django projects
using the DeepL translation API.

Usage:
    python po_translator.py <po_file_path> <source_lang> <target_lang> [--api-key <deepl_api_key>]

Example:
    python po_translator.py locale/es/LC_MESSAGES/django.po en es --api-key YOUR_DEEPL_API_KEY

Requirements:
    - polib: For handling PO files
    - deepl: Official DeepL Python library
"""

import argparse
import os
import sys
import re
import polib
import deepl
from typing import Dict, List, Optional, Tuple


class DeepLTranslator:
    """Class to handle translations using the DeepL API."""

    def __init__(self, api_key: str):
        """
        Initialize the DeepL translator with the API key.

        Args:
            api_key: DeepL API key
        """
        self.translator = deepl.Translator(api_key)

    def _extract_format_placeholders(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extract format placeholders from text to prevent them from being translated.

        Handles both {variable} format and %(variable)s format.

        Args:
            text: Text that may contain format placeholders

        Returns:
            Tuple containing:
                - Text with placeholders replaced by unique markers
                - Dictionary mapping markers back to original placeholders
        """
        # Dictionary to store placeholders and their replacements
        placeholders = {}

        # Process {variable} format (Python format and f-strings)
        brace_pattern = r'(\{[^{}]*\})'
        brace_matches = re.finditer(brace_pattern, text)

        processed_text = text
        for i, match in enumerate(brace_matches):
            placeholder = match.group(0)
            marker = f"__FORMAT_BRACE_{i}__"
            placeholders[marker] = placeholder
            processed_text = processed_text.replace(placeholder, marker, 1)

        # Process %(variable)s format (old-style Python formatting)
        percent_pattern = r'(%\([^()]*\)[diouxXeEfFgGcrs])'
        percent_matches = re.finditer(percent_pattern, processed_text)

        for i, match in enumerate(percent_matches):
            placeholder = match.group(0)
            marker = f"__FORMAT_PERCENT_{i}__"
            placeholders[marker] = placeholder
            processed_text = processed_text.replace(placeholder, marker, 1)

        return processed_text, placeholders

    def _restore_format_placeholders(self, text: str, placeholders: Dict[str, str]) -> str:
        """
        Restore format placeholders in translated text.

        Args:
            text: Translated text with placeholder markers
            placeholders: Dictionary mapping markers to original placeholders

        Returns:
            Text with original placeholders restored
        """
        result = text
        for marker, placeholder in placeholders.items():
            result = result.replace(marker, placeholder)
        return result

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate a single text using DeepL API.

        Preserves format placeholders like {variable} and %(variable)s during translation.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')

        Returns:
            Translated text or None if translation failed
        """
        if not text.strip():
            return text

        try:
            # Extract format placeholders before translation
            processed_text, placeholders = self._extract_format_placeholders(text)

            # Translate the text with placeholders replaced by markers
            result = self.translator.translate_text(
                processed_text, 
                source_lang=source_lang, 
                target_lang=target_lang
            )

            # Restore the original placeholders in the translated text
            translated_text = self._restore_format_placeholders(result.text, placeholders)

            return translated_text
        except Exception as e:
            print(f"Error translating text: {e}", file=sys.stderr)
            return None

    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[Optional[str]]:
        """
        Translate a batch of texts using DeepL API.

        Preserves format placeholders like {variable} and %(variable)s during translation.

        Args:
            texts: List of texts to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')

        Returns:
            List of translated texts (None for failed translations)
        """
        # Filter out empty strings to avoid unnecessary API calls
        non_empty_indices = [i for i, text in enumerate(texts) if text.strip()]
        non_empty_texts = [texts[i] for i in non_empty_indices]

        if not non_empty_texts:
            return texts

        try:
            # Process each text to extract format placeholders
            processed_texts = []
            placeholders_list = []

            for text in non_empty_texts:
                processed_text, placeholders = self._extract_format_placeholders(text)
                processed_texts.append(processed_text)
                placeholders_list.append(placeholders)

            # Translate the processed texts
            results = self.translator.translate_text(
                processed_texts,
                source_lang=source_lang,
                target_lang=target_lang
            )

            # Create a result list with the same size as the input
            translated_texts = texts.copy()

            # Restore placeholders in each translated text
            for i, (idx, result) in enumerate(zip(non_empty_indices, results)):
                translated_text = self._restore_format_placeholders(result.text, placeholders_list[i])
                translated_texts[idx] = translated_text

            return translated_texts
        except Exception as e:
            print(f"Error translating batch: {e}", file=sys.stderr)
            return [None] * len(texts)


class POFileTranslator:
    """Class to handle translation of PO files."""

    def __init__(self, translator: DeepLTranslator):
        """
        Initialize the PO file translator.

        Args:
            translator: DeepL translator instance
        """
        self.translator = translator

    def translate_po_file(self, po_file_path: str, source_lang: str, target_lang: str) -> bool:
        """
        Translate a PO file.

        Args:
            po_file_path: Path to the PO file
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            True if translation was successful, False otherwise
        """
        try:
            # Load the PO file
            po = polib.pofile(po_file_path)

            # Count untranslated entries
            untranslated_count = len([e for e in po if not e.translated()])
            print(f"Found {untranslated_count} untranslated entries in {po_file_path}")

            if untranslated_count == 0:
                print("No untranslated entries found. Exiting.")
                return True

            # Translate untranslated entries
            for entry in po:
                if not entry.translated():
                    # Skip entries with plural forms for now (more complex handling)
                    if entry.msgid_plural:
                        print(f"Skipping plural form: {entry.msgid} (plural forms require manual translation)")
                        continue

                    # Translate the msgid
                    translated_text = self.translator.translate_text(
                        entry.msgid, source_lang, target_lang
                    )

                    if translated_text:
                        entry.msgstr = translated_text
                        print(f"Translated: {entry.msgid} -> {translated_text}")
                    else:
                        print(f"Failed to translate: {entry.msgid}")

            # Save the translated PO file
            po.save()
            print(f"Translated PO file saved to {po_file_path}")
            return True

        except Exception as e:
            print(f"Error translating PO file: {e}", file=sys.stderr)
            return False


def main():
    """Main function to parse arguments and run the translator."""
    parser = argparse.ArgumentParser(description="Translate PO files using DeepL API")
    parser.add_argument("po_file", help="Path to the PO file to translate")
    parser.add_argument("source_lang", help="Source language code (e.g., 'en')")
    parser.add_argument("target_lang", help="Target language code (e.g., 'es')")
    parser.add_argument("--api-key", help="DeepL API key (or set DEEPL_API_KEY environment variable)")

    args = parser.parse_args()

    # Get API key from arguments or environment variable
    api_key = args.api_key or os.environ.get("DEEPL_API_KEY")
    if not api_key:
        print("Error: DeepL API key is required. Provide it with --api-key or set DEEPL_API_KEY environment variable.", 
              file=sys.stderr)
        return 1

    # Check if the PO file exists
    if not os.path.isfile(args.po_file):
        print(f"Error: PO file not found: {args.po_file}", file=sys.stderr)
        return 1

    # Initialize the translator and translate the PO file
    translator = DeepLTranslator(api_key)
    po_translator = POFileTranslator(translator)

    success = po_translator.translate_po_file(args.po_file, args.source_lang, args.target_lang)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
