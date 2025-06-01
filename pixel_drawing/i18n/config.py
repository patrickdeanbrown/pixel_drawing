"""Language configuration for internationalization system."""

from dataclasses import dataclass
from typing import List


@dataclass
class LanguageConfig:
    """Configuration for supported languages.
    
    Attributes:
        code: Language code (e.g., 'en_US', 'es_ES')
        name: English name of the language
        native_name: Native name of the language
        is_rtl: Whether the language is right-to-left
        fallback: Fallback language code if translation missing
    """
    code: str
    name: str
    native_name: str
    is_rtl: bool = False
    fallback: str = "en_US"


# Supported languages configuration
SUPPORTED_LANGUAGES: List[LanguageConfig] = [
    LanguageConfig("en_US", "English", "English"),
    LanguageConfig("es_ES", "Spanish", "Español"), 
    LanguageConfig("fr_FR", "French", "Français"),
    LanguageConfig("de_DE", "German", "Deutsch"),
    LanguageConfig("ja_JP", "Japanese", "日本語"),
    LanguageConfig("zh_CN", "Chinese (Simplified)", "中文(简体)"),
    LanguageConfig("ar_SA", "Arabic", "العربية", is_rtl=True),
]

# Default language
DEFAULT_LANGUAGE = "en_US"

# Language code to configuration mapping
LANGUAGE_MAP = {lang.code: lang for lang in SUPPORTED_LANGUAGES}


def get_language_config(code: str) -> LanguageConfig:
    """Get language configuration by code.
    
    Args:
        code: Language code
        
    Returns:
        LanguageConfig for the language, or default if not found
    """
    return LANGUAGE_MAP.get(code, LANGUAGE_MAP[DEFAULT_LANGUAGE])


def is_language_supported(code: str) -> bool:
    """Check if language code is supported.
    
    Args:
        code: Language code to check
        
    Returns:
        True if language is supported, False otherwise
    """
    return code in LANGUAGE_MAP