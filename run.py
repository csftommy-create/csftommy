"""Convenience launcher: `python run.py`. Also the PyInstaller entry point."""
import sys

from marksix_analyzer.main import main

if __name__ == "__main__":
    sys.exit(main())
