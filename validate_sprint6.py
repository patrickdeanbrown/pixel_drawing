#!/usr/bin/env python3
"""
Sprint 6 Validation Script
Tests all Sprint 6 fixes and enhancements for correctness
"""

import os
import sys
import ast
import importlib.util
from typing import List, Dict, Any

def validate_syntax(file_path: str) -> bool:
    """Validate Python syntax for a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_logging_integration() -> Dict[str, bool]:
    """Check that logging is properly integrated."""
    results = {}
    
    # Files that should have logging integration
    target_files = [
        'pixel_drawing/utils/logging.py',
        'pixel_drawing/views/main_window.py',
        'pixel_drawing/views/canvas.py',
        'pixel_drawing/services/file_service.py',
        'pixel_drawing/controllers/tools/manager.py',
        'pixel_drawing/models/pixel_art_model.py',
        'pixel_drawing/utils/cursors.py',
        'pixel_drawing/utils/icon_cache.py',
        'pixel_drawing/utils/icon_effects.py',
        'pixel_drawing/__main__.py'
    ]
    
    for file_path in target_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for logging imports
                has_logging_import = any([
                    'from .logging import' in content,
                    'from ..utils.logging import' in content,
                    'from ...utils.logging import' in content,
                    'from pixel_drawing.utils.logging import' in content
                ])
                
                # Check for logging function calls
                has_logging_calls = any([
                    'log_info(' in content,
                    'log_debug(' in content,
                    'log_warning(' in content,
                    'log_error(' in content,
                    'log_performance(' in content,
                    'log_canvas_event(' in content,
                    'log_tool_usage(' in content,
                    'log_file_operation(' in content
                ])
                
                results[file_path] = has_logging_import or has_logging_calls
                
            except Exception as e:
                print(f"❌ Error checking logging in {file_path}: {e}")
                results[file_path] = False
        else:
            print(f"❌ File not found: {file_path}")
            results[file_path] = False
    
    return results

def check_css_fixes() -> bool:
    """Check that CSS fixes are implemented."""
    main_window_path = 'pixel_drawing/views/main_window.py'
    
    if not os.path.exists(main_window_path):
        print(f"❌ Main window file not found: {main_window_path}")
        return False
    
    try:
        with open(main_window_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that box-shadow and transform are not used
        has_box_shadow = 'box-shadow' in content
        has_transform = 'transform:' in content
        
        # Check that Qt-compatible properties are used
        has_border_width = 'border-width' in content
        has_margin = 'margin:' in content
        
        if has_box_shadow or has_transform:
            print(f"❌ CSS fix incomplete: Found unsupported properties in {main_window_path}")
            return False
        
        if not (has_border_width and has_margin):
            print(f"❌ CSS fix incomplete: Missing Qt-compatible properties in {main_window_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking CSS fixes: {e}")
        return False

def check_zoom_fixes() -> bool:
    """Check that zoom functionality fixes are implemented."""
    canvas_path = 'pixel_drawing/views/canvas.py'
    
    if not os.path.exists(canvas_path):
        print(f"❌ Canvas file not found: {canvas_path}")
        return False
    
    try:
        with open(canvas_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that DirtyRegionManager is recreated on zoom
        has_dirty_region_update = 'DirtyRegionManager(' in content and 'new_pixel_size' in content
        
        # Check for coordinate logging  
        has_coordinate_logging = 'pixel_size=' in content and 'log_' in content
        
        if not has_dirty_region_update:
            print(f"❌ Zoom fix incomplete: DirtyRegionManager not updated on zoom")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking zoom fixes: {e}")
        return False

def check_icon_fixes() -> bool:
    """Check that icon visibility fixes are implemented."""
    icon_effects_path = 'pixel_drawing/utils/icon_effects.py'
    main_window_path = 'pixel_drawing/views/main_window.py'
    
    if not os.path.exists(icon_effects_path):
        print(f"❌ Icon effects file not found: {icon_effects_path}")
        return False
    
    try:
        with open(icon_effects_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for stateful icon creation
        has_stateful_icons = 'create_icon_with_states' in content
        has_white_icons = 'create_white_icon' in content or 'white' in content
        
        if not (has_stateful_icons and has_white_icons):
            print(f"❌ Icon fix incomplete: Missing stateful icon support")
            return False
        
        # Check main window uses stateful icons
        with open(main_window_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        has_tool_icon_usage = 'get_tool_icon(' in main_content
        
        if not has_tool_icon_usage:
            print(f"❌ Icon fix incomplete: Main window not using stateful icons")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking icon fixes: {e}")
        return False

def check_performance_monitoring() -> bool:
    """Check that performance monitoring is implemented."""
    file_service_path = 'pixel_drawing/services/file_service.py'
    canvas_path = 'pixel_drawing/views/canvas.py'
    
    files_to_check = [file_service_path, canvas_path]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for performance monitoring
            has_time_import = 'import time' in content
            has_timing = 'time.time()' in content
            has_perf_logging = 'log_performance(' in content
            
            if not (has_time_import and has_timing and has_perf_logging):
                print(f"❌ Performance monitoring incomplete in {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking performance monitoring: {e}")
            return False
    
    return True

def run_validation() -> bool:
    """Run all Sprint 6 validation tests."""
    print("🧪 Running Sprint 6 Validation Tests...")
    print("=" * 50)
    
    all_passed = True
    
    # 1. Syntax validation
    print("\n📝 Checking Python syntax...")
    python_files = []
    for root, dirs, files in os.walk('pixel_drawing'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    syntax_passed = True
    for file_path in python_files:
        if not validate_syntax(file_path):
            syntax_passed = False
    
    if syntax_passed:
        print("✅ All Python files have valid syntax")
    else:
        print("❌ Syntax validation failed")
        all_passed = False
    
    # 2. Logging integration
    print("\n📊 Checking logging integration...")
    logging_results = check_logging_integration()
    logging_passed = all(logging_results.values())
    
    if logging_passed:
        print("✅ Logging integration complete")
    else:
        print("❌ Logging integration incomplete:")
        for file_path, result in logging_results.items():
            if not result:
                print(f"  - {file_path}")
        all_passed = False
    
    # 3. CSS fixes
    print("\n🎨 Checking CSS fixes...")
    css_passed = check_css_fixes()
    if css_passed:
        print("✅ CSS fixes implemented")
    else:
        all_passed = False
    
    # 4. Zoom fixes
    print("\n🔍 Checking zoom fixes...")
    zoom_passed = check_zoom_fixes()
    if zoom_passed:
        print("✅ Zoom fixes implemented")
    else:
        all_passed = False
    
    # 5. Icon fixes
    print("\n🎯 Checking icon fixes...")
    icon_passed = check_icon_fixes()
    if icon_passed:
        print("✅ Icon fixes implemented")
    else:
        all_passed = False
    
    # 6. Performance monitoring
    print("\n⚡ Checking performance monitoring...")
    perf_passed = check_performance_monitoring()
    if perf_passed:
        print("✅ Performance monitoring implemented")
    else:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL SPRINT 6 VALIDATION TESTS PASSED!")
        print("✅ Ready for production deployment")
    else:
        print("❌ Some validation tests failed")
        print("🔧 Please review and fix issues above")
    
    return all_passed

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)