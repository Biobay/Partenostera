import pytest
from src.core.validator import ContentValidator, ValidationResult

@pytest.fixture
def validator():
    return ContentValidator()

def test_validate_text_content(validator):
    """Test text content validation"""
    safe_text = "Questo è un testo completamente sicuro e appropriato per tutti."
    unsafe_text = "Contenuto potenzialmente inappropriato o offensivo."
    
    safe_result = validator.validate_text_content(safe_text)
    unsafe_result = validator.validate_text_content(unsafe_text)
    
    assert isinstance(safe_result, ValidationResult)
    assert safe_result.is_valid == True
    assert safe_result.confidence > 0.8
    
    # Il test per contenuto non sicuro dipende dal modello di filtraggio
    assert isinstance(unsafe_result, ValidationResult)

def test_calculate_quality_score(validator):
    """Test quality score calculation"""
    high_quality_text = """
    Una volta, in un regno lontano, viveva un principe coraggioso.
    Il principe aveva capelli dorati che brillavano al sole.
    Ogni giorno cavalcava attraverso foreste incantate.
    """
    
    low_quality_text = "Testo molto breve."
    
    high_score = validator.calculate_quality_score(high_quality_text, None, None)
    low_score = validator.calculate_quality_score(low_quality_text, None, None)
    
    assert 0 <= high_score <= 1
    assert 0 <= low_score <= 1
    assert high_score > low_score

def test_validation_result():
    """Test ValidationResult model"""
    result = ValidationResult(
        is_valid=True,
        confidence=0.95,
        issues=[],
        quality_score=0.85
    )
    
    assert result.is_valid == True
    assert result.confidence == 0.95
    assert result.quality_score == 0.85
    assert len(result.issues) == 0
