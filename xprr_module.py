

#!/usr/bin/env python3
"""
XPRR Module Entry Point
This module serves as the entry point for the xprr command
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main function from the xprr script
if __name__ == "__main__":
    # Import the main function from the xprr script
    exec(open('xprr').read()) 