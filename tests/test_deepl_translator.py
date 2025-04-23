import pytest
import deepl
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
