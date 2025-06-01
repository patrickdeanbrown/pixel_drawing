# Internationalization (I18N) System Design

## Overview

This document outlines the comprehensive internationalization (I18N) system architecture for the Pixel Drawing application. The system is designed to support multiple languages while maintaining code readability and providing easy translation management.

## Architecture Principles

### 1. **Separation of Concerns**
- UI strings separated from business logic
- Centralized translation management
- Runtime language switching capability

### 2. **Qt Integration**
- Leverage Qt's built-in i18n framework (QTranslator)
- Use Qt Linguist tools for professional translation workflow
- Support for right-to-left (RTL) languages

### 3. **Developer Experience**
- Minimal code changes for existing strings
- Type-safe translation keys
- Compile-time validation of translation strings

### 4. **Maintainability**
- Automatic string extraction
- Translation validation and completeness checking
- Version control friendly translation files

## System Components

### 1. Translation Manager (`i18n/manager.py`)

```python
class TranslationManager:
    """Central manager for application translations."""
    
    def __init__(self):
        self._current_locale: str = "en_US"
        self._translators: Dict[str, QTranslator] = {}
        self._app: Optional[QApplication] = None
    
    def initialize(self, app: QApplication) -> None:
        """Initialize translation system with Qt application."""
    
    def set_language(self, locale: str) -> bool:
        """Change application language at runtime."""
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available translation languages."""
    
    def translate(self, context: str, key: str, **kwargs) -> str:
        """Translate string with optional formatting."""
```

### 2. Translation Context Enums (`i18n/contexts.py`)

```python
class UIContext:
    """UI element translation contexts."""
    WINDOW_TITLES = "window_titles"
    TOOLBAR = "toolbar"
    TOOLS = "tools"
    PANELS = "panels"
    DIALOGS = "dialogs"
    STATUS = "status"
    ERRORS = "errors"

class TranslationKey:
    """Type-safe translation key definitions."""
    
    class WindowTitles:
        APP_TITLE = "app_title"
        APP_WITH_FILE = "app_with_file"
    
    class Toolbar:
        NEW = "new"
        OPEN = "open"
        SAVE = "save"
        SAVE_AS = "save_as"
        EXPORT_PNG = "export_png"
        UNDO = "undo" 
        REDO = "redo"
    
    class Tools:
        BRUSH = "brush"
        BRUSH_TOOLTIP = "brush_tooltip"
        FILL = "fill"
        FILL_TOOLTIP = "fill_tooltip"
        ERASER = "eraser"
        ERASER_TOOLTIP = "eraser_tooltip"
        COLOR_PICKER = "color_picker"
        COLOR_PICKER_TOOLTIP = "color_picker_tooltip"
        PAN = "pan"
        PAN_TOOLTIP = "pan_tooltip"
```

### 3. Translation Helper Functions (`i18n/helpers.py`)

```python
def tr(context: str, key: str, **kwargs) -> str:
    """Primary translation function with formatting support."""
    return TranslationManager.instance().translate(context, key, **kwargs)

def tr_tool(key: str, **kwargs) -> str:
    """Shortcut for tool translations."""
    return tr(UIContext.TOOLS, key, **kwargs)

def tr_dialog(key: str, **kwargs) -> str:
    """Shortcut for dialog translations."""
    return tr(UIContext.DIALOGS, key, **kwargs)

def tr_error(key: str, **kwargs) -> str:
    """Shortcut for error message translations."""
    return tr(UIContext.ERRORS, key, **kwargs)
```

### 4. Language Configuration (`i18n/config.py`)

```python
@dataclass
class LanguageConfig:
    """Configuration for supported languages."""
    code: str
    name: str
    native_name: str
    is_rtl: bool = False
    fallback: str = "en_US"

SUPPORTED_LANGUAGES = [
    LanguageConfig("en_US", "English", "English"),
    LanguageConfig("es_ES", "Spanish", "Español"), 
    LanguageConfig("fr_FR", "French", "Français"),
    LanguageConfig("de_DE", "German", "Deutsch"),
    LanguageConfig("ja_JP", "Japanese", "日本語"),
    LanguageConfig("zh_CN", "Chinese (Simplified)", "中文(简体)"),
    LanguageConfig("ar_SA", "Arabic", "العربية", is_rtl=True),
]
```

## File Structure

```
pixel_drawing/
├── i18n/
│   ├── __init__.py
│   ├── manager.py          # Translation manager
│   ├── contexts.py         # Translation contexts and keys
│   ├── helpers.py          # Helper functions
│   ├── config.py           # Language configuration
│   ├── translations/       # Translation files
│   │   ├── en_US.ts       # English (source)
│   │   ├── es_ES.ts       # Spanish
│   │   ├── fr_FR.ts       # French
│   │   ├── de_DE.ts       # German
│   │   ├── ja_JP.ts       # Japanese
│   │   ├── zh_CN.ts       # Chinese
│   │   └── ar_SA.ts       # Arabic
│   └── compiled/           # Compiled .qm files
│       ├── en_US.qm
│       ├── es_ES.qm
│       └── ...
└── constants.py            # Updated with i18n keys
```

## Translation Files Format

### English Source File (`translations/en_US.ts`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">
<context>
    <name>window_titles</name>
    <message>
        <source>app_title</source>
        <translation>Pixel Drawing - Retro Game Asset Creator</translation>
    </message>
    <message>
        <source>app_with_file</source>
        <translation>Pixel Drawing - %1</translation>
    </message>
</context>
<context>
    <name>toolbar</name>
    <message>
        <source>new</source>
        <translation>New</translation>
    </message>
    <message>
        <source>open</source>
        <translation>Open</translation>
    </message>
    <message>
        <source>save</source>
        <translation>Save</translation>
    </message>
</context>
<context>
    <name>tools</name>
    <message>
        <source>brush</source>
        <translation>Brush</translation>
    </message>
    <message>
        <source>brush_tooltip</source>
        <translation>Brush Tool (B)</translation>
    </message>
</context>
</TS>
```

## Implementation Strategy

### Phase 1: Foundation (Sprint 8)
1. **Create I18N system infrastructure**
   - Translation manager implementation
   - Context and key definitions
   - Helper function library
   - Build system integration

2. **Update constants.py**
   - Replace hardcoded strings with translation keys
   - Maintain backward compatibility during transition

### Phase 2: Core UI Integration (Sprint 9)
1. **Update main window components**
   - Replace all UI strings with tr() calls
   - Implement language switching in settings
   - Add language selection to preferences

2. **Tool system integration**
   - Update all tool classes with i18n
   - Ensure tooltip translations work correctly

### Phase 3: Advanced Features (Sprint 10)
1. **Runtime language switching**
   - Implement UI refresh on language change
   - Save language preference to user settings
   - Handle RTL language support

2. **Translation workflow**
   - Set up automated string extraction
   - Create translation validation scripts
   - Documentation for translators

## Code Migration Example

### Before (Current)
```python
# main_window.py
self.new_action = QAction("New", self)
self.open_action = QAction("Open", self)
clear_btn = QPushButton("Clear Canvas")
```

### After (With I18N)
```python
# main_window.py
from ..i18n.helpers import tr_toolbar, tr_dialog
from ..i18n.contexts import UIContext, TranslationKey

self.new_action = QAction(tr_toolbar(TranslationKey.Toolbar.NEW), self)
self.open_action = QAction(tr_toolbar(TranslationKey.Toolbar.OPEN), self)
clear_btn = QPushButton(tr_dialog(TranslationKey.Dialogs.CLEAR_CANVAS))
```

## Qt Linguist Integration

### String Extraction
```bash
# Extract translatable strings from source code
pylupdate6 pixel_drawing/**/*.py -ts i18n/translations/en_US.ts

# Update existing translation files
pylupdate6 pixel_drawing/**/*.py -ts i18n/translations/*.ts
```

### Translation Compilation
```bash
# Compile .ts files to .qm for runtime use
lrelease i18n/translations/*.ts

# Automated build integration
python setup.py build_translations
```

## User Experience Features

### 1. Language Selection
- Settings dialog with language dropdown
- Native language names displayed
- Instant preview of changes
- Restart notification if needed

### 2. RTL Language Support
- Automatic layout direction switching
- Icon mirroring for directional elements
- Text alignment adjustments

### 3. Fallback Behavior
- Graceful degradation to English if translation missing
- Logging of untranslated strings for debugging
- Development mode warnings for missing translations

## Testing Strategy

### 1. Translation Completeness
```python
def test_translation_completeness():
    """Verify all translation files have complete coverage."""
    for lang in SUPPORTED_LANGUAGES:
        assert check_translation_coverage(lang.code) >= 0.95
```

### 2. UI Layout Testing
```python
def test_ui_layout_with_long_translations():
    """Test UI remains functional with long German/Finnish text."""
    set_test_language("de_DE")
    assert all_buttons_visible()
    assert no_text_overflow()
```

### 3. RTL Testing
```python
def test_rtl_layout():
    """Test right-to-left language support."""
    set_test_language("ar_SA")
    assert layout_direction_is_rtl()
    assert toolbar_buttons_mirrored()
```

## Performance Considerations

### 1. Translation Caching
- Cache translated strings to avoid repeated lookups
- Invalidate cache on language changes
- Memory-efficient string interpolation

### 2. Lazy Loading
- Load only active language translations
- Background loading of additional languages
- Minimize startup time impact

### 3. File Size Optimization
- Compress .qm files in distribution
- Remove unused translations from builds
- Optimize string storage format

## Future Enhancements

### 1. Pluralization Support
- Handle singular/plural forms correctly
- Support complex plural rules (Russian, Arabic)
- Numeric formatting localization

### 2. Date/Time Localization
- Format timestamps according to locale
- Support different calendar systems
- Time zone handling improvements

### 3. Cultural Adaptations
- Color scheme preferences by culture
- Different default canvas sizes
- Region-specific file format preferences

## Conclusion

This I18N system provides a robust foundation for internationalization while maintaining code quality and developer productivity. The architecture supports both immediate needs and future expansion to additional languages and localization features.

The system leverages Qt's proven i18n infrastructure while adding modern development conveniences like type-safe keys and automated tooling integration.