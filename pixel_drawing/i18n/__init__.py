"""Internationalization (I18N) system for Pixel Drawing application.

This module provides comprehensive internationalization support including:
- Translation management and runtime language switching
- Type-safe translation keys and contexts
- Qt Linguist integration for professional translation workflow
- Support for RTL languages and cultural adaptations

Usage:
    from pixel_drawing.i18n import tr, tr_tool, tr_dialog
    
    # Basic translation
    text = tr("toolbar", "new")
    
    # Tool-specific translation  
    tool_name = tr_tool("brush")
    
    # Dialog translation with formatting
    message = tr_dialog("save_error", filename="test.json")
"""

from .manager import TranslationManager
from .helpers import tr, tr_window, tr_toolbar, tr_tool, tr_panel, tr_dialog, tr_error, tr_status, tr_filter, tr_pref
from .contexts import UIContext, TranslationKey
from .config import SUPPORTED_LANGUAGES, LanguageConfig

__all__ = [
    "TranslationManager",
    "tr", "tr_window", "tr_toolbar", "tr_tool", "tr_panel", "tr_dialog", "tr_error", "tr_status", "tr_filter", "tr_pref",
    "UIContext", "TranslationKey", 
    "SUPPORTED_LANGUAGES", "LanguageConfig"
]