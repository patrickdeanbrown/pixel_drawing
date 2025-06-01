"""Helper functions for internationalization."""

from .manager import TranslationManager
from .contexts import UIContext


def tr(context: str, key: str, **kwargs) -> str:
    """Primary translation function with formatting support.
    
    Args:
        context: Translation context (e.g., 'toolbar', 'dialogs')
        key: Translation key
        **kwargs: Formatting arguments for string interpolation
        
    Returns:
        Translated and formatted string
        
    Example:
        tr("dialogs", "save_error", filename="test.json")
    """
    return TranslationManager.instance().translate(context, key, **kwargs)


def tr_window(key: str, **kwargs) -> str:
    """Shortcut for window title translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.WINDOW_TITLES, key, **kwargs)


def tr_toolbar(key: str, **kwargs) -> str:
    """Shortcut for toolbar action translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.TOOLBAR, key, **kwargs)


def tr_tool(key: str, **kwargs) -> str:
    """Shortcut for tool translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.TOOLS, key, **kwargs)


def tr_panel(key: str, **kwargs) -> str:
    """Shortcut for panel and label translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.PANELS, key, **kwargs)


def tr_dialog(key: str, **kwargs) -> str:
    """Shortcut for dialog translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.DIALOGS, key, **kwargs)


def tr_status(key: str, **kwargs) -> str:
    """Shortcut for status message translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.STATUS, key, **kwargs)


def tr_error(key: str, **kwargs) -> str:
    """Shortcut for error message translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.ERRORS, key, **kwargs)


def tr_filter(key: str, **kwargs) -> str:
    """Shortcut for file filter translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.FILE_FILTERS, key, **kwargs)


def tr_pref(key: str, **kwargs) -> str:
    """Shortcut for preferences dialog translations.
    
    Args:
        key: Translation key
        **kwargs: Formatting arguments
        
    Returns:
        Translated string
    """
    return tr(UIContext.PREFERENCES, key, **kwargs)