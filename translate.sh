#!/bin/bash

echo "PO File Translator for Django Projects"
echo "======================================"
echo

if [ $# -lt 3 ]; then
    echo "Usage: ./translate.sh <po_file> <source_lang> <target_lang> [api_key]"
    echo
    echo "Examples:"
    echo "  ./translate.sh example.po en es YOUR_API_KEY"
    echo "  ./translate.sh locale/es/LC_MESSAGES/django.po en es YOUR_API_KEY"
    echo
    echo "Note: You can also set the DEEPL_API_KEY environment variable instead of providing the API key as a parameter."
    exit 1
fi

PO_FILE=$1
SOURCE_LANG=$2
TARGET_LANG=$3

if [ -z "$4" ]; then
    if [ -z "$DEEPL_API_KEY" ]; then
        echo "Error: DeepL API key is required."
        echo "Either provide it as the fourth parameter or set the DEEPL_API_KEY environment variable."
        exit 1
    fi
    python po_translator.py "$PO_FILE" "$SOURCE_LANG" "$TARGET_LANG"
else
    python po_translator.py "$PO_FILE" "$SOURCE_LANG" "$TARGET_LANG" --api-key "$4"
fi
