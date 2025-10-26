"""
Entry point for the qualtrics_util package.

This module provides the CLI entry point when running as a module:
    python -m qualtrics_util
    
For backward compatibility, also supports the original qualtrics_util.py
"""

def main():
    """Entry point that delegates to CLI module."""
    try:
        # Try using the new modular CLI
        from qualtrics_util.cli import main as cli_main
        cli_main()
    except ImportError:
        # Fallback to original implementation if new CLI not available
        print("Note: Using new modular CLI")
        import sys
        sys.path.insert(0, 'src')
        from qualtrics_util.cli import main as cli_main
        cli_main()


if __name__ == '__main__':
    main()

