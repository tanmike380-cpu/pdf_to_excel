"""Cleanup service for temp files."""

import time
import os
from pathlib import Path
from typing import List

from app.utils.temp_files import TEMP_DIR, EXCEL_DIR, cleanup_all
from app.core.logger import get_logger

logger = get_logger("cleanup_service")

# Files older than this (seconds) will be cleaned up
MAX_AGE_SECONDS = 3600  # 1 hour


def cleanup_old_files(max_age: int = MAX_AGE_SECONDS) -> int:
    """
    Clean up files older than max_age seconds.
    Returns number of files/dirs removed.
    """
    removed = 0
    now = time.time()
    
    # Clean temp dirs
    if TEMP_DIR.exists():
        for item in TEMP_DIR.iterdir():
            if item.is_dir():
                # Check mtime
                mtime = item.stat().st_mtime
                if now - mtime > max_age:
                    try:
                        import shutil
                        shutil.rmtree(item)
                        logger.info(f"Cleaned up temp dir: {item}")
                        removed += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove {item}: {e}")
    
    # Clean excel files
    if EXCEL_DIR.exists():
        for item in EXCEL_DIR.iterdir():
            if item.is_file() and item.suffix == ".xlsx":
                mtime = item.stat().st_mtime
                if now - mtime > max_age:
                    try:
                        item.unlink()
                        logger.info(f"Cleaned up excel file: {item}")
                        removed += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove {item}: {e}")
    
    return removed


def schedule_cleanup_task():
    """Start a background cleanup task. Call this on app startup."""
    import threading
    
    def cleanup_loop():
        while True:
            time.sleep(600)  # Check every 10 minutes
            try:
                removed = cleanup_old_files()
                if removed:
                    logger.info(f"Cleanup completed: {removed} items removed")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info("Cleanup task started")
