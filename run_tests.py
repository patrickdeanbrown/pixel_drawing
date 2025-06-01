#!/usr/bin/env python3
"""
Test runner script for Pixel Drawing Application.

This script provides convenient commands for running different categories
of tests and generating reports.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🧪 {description}")
    print("=" * 60)
    print(f"Running: {' '.join(command)}")
    print("-" * 60)
    
    result = subprocess.run(command, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
    else:
        print(f"❌ {description} failed with exit code {result.returncode}")
    
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Test runner for Pixel Drawing Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                 # Run all tests
  python run_tests.py --unit          # Run only unit tests
  python run_tests.py --integration   # Run only integration tests
  python run_tests.py --performance   # Run performance tests
  python run_tests.py --coverage      # Run with detailed coverage
  python run_tests.py --fast          # Run fast tests only
  python run_tests.py --lint          # Run linting and type checking
        """
    )
    
    # Test type selection
    parser.add_argument('--unit', action='store_true', 
                       help='Run unit tests only')
    parser.add_argument('--integration', action='store_true',
                       help='Run integration tests only')
    parser.add_argument('--ui', action='store_true',
                       help='Run UI tests only')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    
    # Test configuration
    parser.add_argument('--fast', action='store_true',
                       help='Run fast tests only (exclude slow marker)')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate detailed coverage report')
    parser.add_argument('--benchmark', action='store_true',
                       help='Include benchmark tests')
    parser.add_argument('--parallel', type=int, metavar='N',
                       help='Run tests in parallel with N workers')
    
    # Code quality
    parser.add_argument('--lint', action='store_true',
                       help='Run linting and type checking')
    parser.add_argument('--format', action='store_true',
                       help='Format code with black and isort')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet output')
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML test report')
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    # Test selection
    if args.unit:
        pytest_cmd.extend(['-m', 'unit'])
    elif args.integration:
        pytest_cmd.extend(['-m', 'integration'])
    elif args.ui:
        pytest_cmd.extend(['-m', 'ui'])
    elif args.performance:
        pytest_cmd.extend(['-m', 'performance'])
    
    # Speed options
    if args.fast:
        pytest_cmd.extend(['-m', 'not slow'])
    
    # Parallel execution
    if args.parallel:
        pytest_cmd.extend(['-n', str(args.parallel)])
    
    # Benchmark tests
    if args.benchmark:
        pytest_cmd.append('--benchmark-only')
    elif not args.performance:
        pytest_cmd.append('--benchmark-skip')
    
    # Output control
    if args.verbose:
        pytest_cmd.append('-v')
    elif args.quiet:
        pytest_cmd.append('-q')
    
    # Coverage options
    if args.coverage:
        pytest_cmd.extend([
            '--cov=pixel_drawing',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-report=xml'
        ])
    
    # HTML report
    if args.html_report:
        pytest_cmd.extend(['--html=reports/test_report.html', '--self-contained-html'])
    
    exit_code = 0
    
    # Run code formatting if requested
    if args.format:
        format_commands = [
            (['python', '-m', 'black', 'pixel_drawing/', 'tests/'], "Code formatting with black"),
            (['python', '-m', 'isort', 'pixel_drawing/', 'tests/'], "Import sorting with isort")
        ]
        
        for cmd, desc in format_commands:
            result = run_command(cmd, desc)
            exit_code = max(exit_code, result)
    
    # Run linting if requested
    if args.lint:
        lint_commands = [
            (['python', '-m', 'flake8', 'pixel_drawing/', 'tests/'], "Linting with flake8"),
            (['python', '-m', 'mypy', 'pixel_drawing/'], "Type checking with mypy")
        ]
        
        for cmd, desc in lint_commands:
            result = run_command(cmd, desc)
            exit_code = max(exit_code, result)
    
    # Run tests
    if not args.format and not args.lint:
        test_description = "Running tests"
        if args.unit:
            test_description = "Running unit tests"
        elif args.integration:
            test_description = "Running integration tests"
        elif args.ui:
            test_description = "Running UI tests"
        elif args.performance:
            test_description = "Running performance tests"
        
        result = run_command(pytest_cmd, test_description)
        exit_code = max(exit_code, result)
    
    # Summary
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 All operations completed successfully!")
        
        if args.coverage:
            print("\n📊 Coverage report generated: htmlcov/index.html")
        if args.html_report:
            print("📋 Test report generated: reports/test_report.html")
            
    else:
        print("❌ Some operations failed. Check output above for details.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())