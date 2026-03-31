#!/usr/bin/env python3
"""
Automation Tool - Batch automation for repetitive software operations
Main entry point
"""

import sys
import pyautogui # Import pyautogui

pyautogui.FAILSAFE = False # Disable failsafe globally

from gui import MainWindow
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Start the application"""
    try:
        logger.info("Starting Automation Tool...")

        logger.info("Local mode active: operations are stored in automation_data.json")

        # Create and run main window
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
