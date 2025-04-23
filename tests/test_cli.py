import pytest
import sys
import os
from unittest.mock import patch, MagicMock

from po_translator import main


class TestCLI:
    """Tests for the command-line interface."""

    def test_main_missing_api_key(self):
        """Test main function with missing API key."""
        # Mock sys.argv to simulate command-line arguments
        test_args = ["po_translator.py", "test.po", "en", "es"]
        with patch.object(sys, 'argv', test_args):
            # Mock os.environ to ensure DEEPL_API_KEY is not set
            with patch.dict(os.environ, {}, clear=True):
                # Call main and check the return code
                with patch('sys.stderr'):  # Suppress error output
                    result = main()
                    assert result == 1

    def test_main_nonexistent_file(self, api_key):
        """Test main function with a non-existent PO file."""
        # Mock sys.argv to simulate command-line arguments
        test_args = ["po_translator.py", "nonexistent.po", "en", "es", "--api-key", api_key]
        with patch.object(sys, 'argv', test_args):
            # Call main and check the return code
            with patch('sys.stderr'):  # Suppress error output
                result = main()
                assert result == 1

    def test_main_success(self, api_key, sample_po_file):
        """Test successful execution of main function."""
        # Mock sys.argv to simulate command-line arguments
        test_args = ["po_translator.py", sample_po_file, "en", "es", "--api-key", api_key]
        
        # Mock the DeepLTranslator and POFileTranslator classes
        with patch('po_translator.DeepLTranslator') as mock_deepl_translator_cls:
            mock_deepl_translator = MagicMock()
            mock_deepl_translator_cls.return_value = mock_deepl_translator
            
            with patch('po_translator.POFileTranslator') as mock_po_translator_cls:
                mock_po_translator = MagicMock()
                mock_po_translator.translate_po_file.return_value = True
                mock_po_translator_cls.return_value = mock_po_translator
                
                with patch.object(sys, 'argv', test_args):
                    result = main()
                    
                    # Check that the translator was initialized with the correct API key
                    mock_deepl_translator_cls.assert_called_once_with(api_key)
                    
                    # Check that the PO translator was initialized with the DeepL translator
                    mock_po_translator_cls.assert_called_once_with(mock_deepl_translator)
                    
                    # Check that translate_po_file was called with the correct arguments
                    mock_po_translator.translate_po_file.assert_called_once_with(
                        sample_po_file, "en", "es"
                    )
                    
                    # Check the return code
                    assert result == 0

    def test_main_translation_failure(self, api_key, sample_po_file):
        """Test main function when translation fails."""
        # Mock sys.argv to simulate command-line arguments
        test_args = ["po_translator.py", sample_po_file, "en", "es", "--api-key", api_key]
        
        # Mock the DeepLTranslator and POFileTranslator classes
        with patch('po_translator.DeepLTranslator'):
            with patch('po_translator.POFileTranslator') as mock_po_translator_cls:
                mock_po_translator = MagicMock()
                mock_po_translator.translate_po_file.return_value = False
                mock_po_translator_cls.return_value = mock_po_translator
                
                with patch.object(sys, 'argv', test_args):
                    result = main()
                    
                    # Check the return code
                    assert result == 1

    def test_main_with_env_api_key(self, api_key, sample_po_file):
        """Test main function with API key from environment variable."""
        # Mock sys.argv to simulate command-line arguments without --api-key
        test_args = ["po_translator.py", sample_po_file, "en", "es"]
        
        # Mock the DeepLTranslator and POFileTranslator classes
        with patch('po_translator.DeepLTranslator') as mock_deepl_translator_cls:
            with patch('po_translator.POFileTranslator') as mock_po_translator_cls:
                mock_po_translator = MagicMock()
                mock_po_translator.translate_po_file.return_value = True
                mock_po_translator_cls.return_value = mock_po_translator
                
                # Set the DEEPL_API_KEY environment variable
                with patch.dict(os.environ, {"DEEPL_API_KEY": api_key}):
                    with patch.object(sys, 'argv', test_args):
                        result = main()
                        
                        # Check that the translator was initialized with the correct API key
                        mock_deepl_translator_cls.assert_called_once_with(api_key)
                        
                        # Check the return code
                        assert result == 0
