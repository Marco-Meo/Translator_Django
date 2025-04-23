import pytest
import polib
import os
from unittest.mock import patch, MagicMock

from po_translator import POFileTranslator


class TestPOFileTranslator:
    """Tests for the POFileTranslator class."""

    def test_init(self, mock_deepl_translator):
        """Test initialization of POFileTranslator."""
        translator = POFileTranslator(mock_deepl_translator)
        assert translator.translator == mock_deepl_translator


    def test_translate_po_file_no_untranslated(self, mock_deepl_translator, tmp_path):
        """Test translating a PO file with no untranslated entries."""
        # Create a PO file with all entries already translated
        po_file_path = tmp_path / "test_translated.po"
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': 'Test Project',
            'Language': 'en',
        }
        
        entry = polib.POEntry(
            msgid='Already translated',
            msgstr='Already translated',  # Already translated
            occurrences=[('test.py', '10')]
        )
        po.append(entry)
        po.save(po_file_path)
        
        translator = POFileTranslator(mock_deepl_translator)
        result = translator.translate_po_file(str(po_file_path), "en-us", "es")
        
        assert result is True
        # Verify the translator was not called
        mock_deepl_translator.translate_text.assert_not_called()

    def test_translate_po_file_with_untranslated(self, mock_deepl_translator, sample_po_file):
        """Test translating a PO file with untranslated entries."""
        translator = POFileTranslator(mock_deepl_translator)
        result = translator.translate_po_file(sample_po_file, "en-us", "es")
        
        assert result is True
        
        # Load the translated file and check the translations
        po = polib.pofile(sample_po_file)
        
        # Check that untranslated entries were translated
        for entry in po:
            if entry.msgid == 'Hello, world!':
                assert entry.msgstr == '[es] Hello, world!'
            elif entry.msgid == 'Welcome to our application':
                assert entry.msgstr == '[es] Welcome to our application'
            elif entry.msgid == 'This is already translated':
                assert entry.msgstr == 'This is already translated'  # Should remain unchanged
            elif entry.msgid == '%d item':
                # Plural forms should be skipped
                assert entry.msgstr_plural[0] == ''
                assert entry.msgstr_plural[1] == ''


    def test_translate_po_file_exception(self, mock_deepl_translator):
        """Test exception handling during PO file translation."""
        # Create a mock that raises an exception when polib.pofile is called
        with patch('polib.pofile', side_effect=Exception("File error")):
            translator = POFileTranslator(mock_deepl_translator)
            result = translator.translate_po_file("invalid.po", "en-us", "es")
            
            assert result is False
