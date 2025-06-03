import pytest
from src.core.text_analyzer import TextAnalyzer

@pytest.fixture
def text_analyzer():
    return TextAnalyzer()

def test_extract_sequences(text_analyzer):
    """Test sequence extraction"""
    sample_text = """
    C'era una volta un piccolo principe che abitava su un pianeta. 
    Un giorno decise di partire per un lungo viaggio tra le stelle.
    Durante il viaggio incontrò molti personaggi strani e interessanti.
    Alla fine del suo viaggio, il principe aveva imparato molte cose importanti.
    """
    
    sequences = text_analyzer.extract_sequences(sample_text)
    assert len(sequences) > 0
    assert all('text' in seq for seq in sequences)
    assert all('image_prompt' in seq for seq in sequences)

def test_generate_image_prompt(text_analyzer):
    """Test image prompt generation"""
    text = "Un piccolo principe su un pianeta lontano tra le stelle"
    prompt = text_analyzer.generate_image_prompt(text)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert any(keyword in prompt.lower() for keyword in ['prince', 'planet', 'stars'])

def test_analyze_sentiment(text_analyzer):
    """Test sentiment analysis"""
    positive_text = "Era una giornata meravigliosa e tutti erano felici"
    negative_text = "Era una giornata terribile e tutti erano tristi"
    
    pos_sentiment = text_analyzer.analyze_sentiment(positive_text)
    neg_sentiment = text_analyzer.analyze_sentiment(negative_text)
    
    assert pos_sentiment > neg_sentiment
    assert -1 <= pos_sentiment <= 1
    assert -1 <= neg_sentiment <= 1
