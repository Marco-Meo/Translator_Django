import pytest
import deepl
import re
from unittest.mock import patch, MagicMock

from po_translator import DeepLTranslator


class TestDeepLTranslator:
    """Tests for the DeepLTranslator class."""

    def test_init(self):
        """Test initialization of DeepLTranslator."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator:
            translator = DeepLTranslator(api_key)
            mock_translator.assert_called_once_with(api_key)

    def test_translate_text_empty(self):
        """Test translating empty text."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)
            result = translator.translate_text("", "en-us", "de")
            assert result == ""

    def test_translate_text_success(self):
        """Test successful text translation."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method of the deepl.Translator instance
            mock_result = MagicMock()
            mock_result.text = "Hallo Welt"
            mock_translator.translate_text.return_value = mock_result

            translator = DeepLTranslator(api_key)
            result = translator.translate_text("Hello world", "en-us", "de")

            assert result == "Hallo Welt"
            mock_translator.translate_text.assert_called_once_with(
                "Hello world", source_lang="en-us", target_lang="de"
            )

    def test_translate_text_error(self):
        """Test error handling during text translation."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method to raise an exception
            mock_translator.translate_text.side_effect = Exception("API error")

            translator = DeepLTranslator(api_key)
            result = translator.translate_text("Hello world", "en-us", "de")

            assert result is None

    def test_translate_batch_empty(self):
        """Test translating an empty batch."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)
            result = translator.translate_batch([], "en-us", "de")
            assert result == []

    def test_translate_batch_with_empty_strings(self):
        """Test translating a batch with empty strings."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)
            result = translator.translate_batch(["", "  ", ""], "en-us", "de")
            assert result == ["", "  ", ""]

    def test_translate_batch_success(self):
        """Test successful batch translation."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method for batch translation
            mock_results = [MagicMock(), MagicMock()]
            mock_results[0].text = "Hallo Welt"
            mock_results[1].text = "Willkommen"
            mock_translator.translate_text.return_value = mock_results

            translator = DeepLTranslator(api_key)
            result = translator.translate_batch(["Hello world", "Welcome"], "en-us", "de")

            assert result == ["Hallo Welt", "Willkommen"]
            mock_translator.translate_text.assert_called_once_with(
                ["Hello world", "Welcome"], source_lang="en-us", target_lang="de"
            )

    def test_translate_batch_error(self):
        """Test error handling during batch translation."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method to raise an exception
            mock_translator.translate_text.side_effect = Exception("API error")

            translator = DeepLTranslator(api_key)
            result = translator.translate_batch(["Hello world", "Welcome"], "en-us", "de")

            assert result == [None, None]

    def test_extract_format_placeholders_brace_format(self):
        """Test extracting brace format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)

            # Test with brace format placeholders
            text = "Hello {name}, welcome to {place}!"
            processed_text, placeholders = translator._extract_format_placeholders(text)

            # Check that placeholders were extracted
            assert "{name}" not in processed_text
            assert "{place}" not in processed_text

            # Check that markers were inserted
            assert "__FORMAT_BRACE_0__" in processed_text
            assert "__FORMAT_BRACE_1__" in processed_text

            # Check that placeholders dictionary contains the correct mappings
            assert len(placeholders) == 2
            assert placeholders["__FORMAT_BRACE_0__"] == "{name}"
            assert placeholders["__FORMAT_BRACE_1__"] == "{place}"

    def test_extract_format_placeholders_percent_format(self):
        """Test extracting percent format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)

            # Test with percent format placeholders
            text = "Hello %(name)s, your score is %(score)d!"
            processed_text, placeholders = translator._extract_format_placeholders(text)

            # Check that placeholders were extracted
            assert "%(name)s" not in processed_text
            assert "%(score)d" not in processed_text

            # Check that markers were inserted
            assert "__FORMAT_PERCENT_0__" in processed_text
            assert "__FORMAT_PERCENT_1__" in processed_text

            # Check that placeholders dictionary contains the correct mappings
            assert len(placeholders) == 2
            assert placeholders["__FORMAT_PERCENT_0__"] == "%(name)s"
            assert placeholders["__FORMAT_PERCENT_1__"] == "%(score)d"

    def test_extract_format_placeholders_mixed_format(self):
        """Test extracting mixed format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)

            # Test with both brace and percent format placeholders
            text = "Hello {name}, your score is %(score)d!"
            processed_text, placeholders = translator._extract_format_placeholders(text)

            # Check that placeholders were extracted
            assert "{name}" not in processed_text
            assert "%(score)d" not in processed_text

            # Check that markers were inserted
            assert "__FORMAT_BRACE_0__" in processed_text
            assert "__FORMAT_PERCENT_0__" in processed_text

            # Check that placeholders dictionary contains the correct mappings
            assert len(placeholders) == 2
            assert placeholders["__FORMAT_BRACE_0__"] == "{name}"
            assert placeholders["__FORMAT_PERCENT_0__"] == "%(score)d"

    def test_restore_format_placeholders(self):
        """Test restoring format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator'):
            translator = DeepLTranslator(api_key)

            # Create a text with placeholder markers
            text = "Hallo __FORMAT_BRACE_0__, willkommen bei __FORMAT_BRACE_1__!"
            placeholders = {
                "__FORMAT_BRACE_0__": "{name}",
                "__FORMAT_BRACE_1__": "{place}"
            }

            # Restore placeholders
            restored_text = translator._restore_format_placeholders(text, placeholders)

            # Check that markers were replaced with original placeholders
            assert "__FORMAT_BRACE_0__" not in restored_text
            assert "__FORMAT_BRACE_1__" not in restored_text
            assert "{name}" in restored_text
            assert "{place}" in restored_text
            assert restored_text == "Hallo {name}, willkommen bei {place}!"

    def test_translate_text_with_brace_format(self):
        """Test translating text with brace format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method
            mock_result = MagicMock()
            mock_result.text = "Hallo __FORMAT_BRACE_0__, willkommen bei __FORMAT_BRACE_1__!"
            mock_translator.translate_text.return_value = mock_result

            translator = DeepLTranslator(api_key)
            result = translator.translate_text("Hello {name}, welcome to {place}!", "en-us", "de")

            # Check that the result contains the original placeholders
            assert "{name}" in result
            assert "{place}" in result
            assert result == "Hallo {name}, willkommen bei {place}!"

            # Check that the text sent to DeepL had the placeholders replaced
            args, kwargs = mock_translator.translate_text.call_args
            assert "{name}" not in args[0]
            assert "{place}" not in args[0]

    def test_translate_text_with_percent_format(self):
        """Test translating text with percent format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method
            mock_result = MagicMock()
            mock_result.text = "Hallo __FORMAT_PERCENT_0__, dein Ergebnis ist __FORMAT_PERCENT_1__!"
            mock_translator.translate_text.return_value = mock_result

            translator = DeepLTranslator(api_key)
            result = translator.translate_text("Hello %(name)s, your score is %(score)d!", "en-us", "de")

            # Check that the result contains the original placeholders
            assert "%(name)s" in result
            assert "%(score)d" in result
            assert result == "Hallo %(name)s, dein Ergebnis ist %(score)d!"

            # Check that the text sent to DeepL had the placeholders replaced
            args, kwargs = mock_translator.translate_text.call_args
            assert "%(name)s" not in args[0]
            assert "%(score)d" not in args[0]

    def test_translate_batch_with_format_placeholders(self):
        """Test translating a batch of texts with format placeholders."""
        api_key = "test_api_key"
        with patch('deepl.Translator') as mock_translator_cls:
            mock_translator = MagicMock()
            mock_translator_cls.return_value = mock_translator

            # Mock the translate_text method for batch translation
            mock_results = [MagicMock(), MagicMock()]
            mock_results[0].text = "Hallo __FORMAT_BRACE_0__!"
            mock_results[1].text = "Dein Ergebnis: __FORMAT_PERCENT_0__"
            mock_translator.translate_text.return_value = mock_results

            translator = DeepLTranslator(api_key)
            result = translator.translate_batch(["Hello {name}!", "Your score: %(score)d"], "en-us", "de")

            # Check that the results contain the original placeholders
            assert result[0] == "Hallo {name}!"
            assert result[1] == "Dein Ergebnis: %(score)d"

            # Check that the texts sent to DeepL had the placeholders replaced
            args, kwargs = mock_translator.translate_text.call_args
            assert "{name}" not in args[0][0]
            assert "%(score)d" not in args[0][1]
