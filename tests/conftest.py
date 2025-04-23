import os
import sys
import pytest
import polib
from unittest.mock import MagicMock

# Add the parent directory to sys.path to import po_translator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from po_translator import DeepLTranslator, POFileTranslator


@pytest.fixture
def mock_deepl_translator():
    """Create a mock DeepLTranslator that doesn't make actual API calls."""
    translator = MagicMock(spec=DeepLTranslator)
    
    # Mock the translate_text method
    def mock_translate_text(text, source_lang, target_lang):
        if not text.strip():
            return text
        # Simple mock translation: add a prefix to indicate translation
        return f"[{target_lang}] {text}"
    
    translator.translate_text.side_effect = mock_translate_text
    
    # Mock the translate_batch method
    def mock_translate_batch(texts, source_lang, target_lang):
        return [mock_translate_text(text, source_lang, target_lang) for text in texts]
    
    translator.translate_batch.side_effect = mock_translate_batch
    
    return translator


@pytest.fixture
def sample_po_file(tmp_path):
    """Create a sample PO file for testing."""
    po_file_path = tmp_path / "test.po"
    
    # Create a sample PO file
    po = polib.POFile()
    po.metadata = {
        'Project-Id-Version': 'Test Project',
        'Language': 'en',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }
    
    # Add some entries
    entry1 = polib.POEntry(
        msgid='Hello, world!',
        msgstr='',  # Untranslated
        occurrences=[('test.py', '10')]
    )
    po.append(entry1)
    
    entry2 = polib.POEntry(
        msgid='Welcome to our application',
        msgstr='',  # Untranslated
        occurrences=[('test.py', '20')]
    )
    po.append(entry2)
    
    entry3 = polib.POEntry(
        msgid='This is already translated',
        msgstr='This is already translated',  # Already translated
        occurrences=[('test.py', '30')]
    )
    po.append(entry3)
    
    # Add an entry with plural forms
    entry4 = polib.POEntry(
        msgid='%d item',
        msgid_plural='%d items',
        msgstr_plural={0: '', 1: ''},  # Untranslated plural forms
        occurrences=[('test.py', '40')]
    )
    po.append(entry4)
    
    # Save the PO file
    po.save(po_file_path)
    
    return str(po_file_path)


@pytest.fixture
def api_key():
    """Return a dummy API key for testing."""
    return "dummy_api_key"
