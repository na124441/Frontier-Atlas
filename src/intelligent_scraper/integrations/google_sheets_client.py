"""
Google Sheets Client.
Provides connection to Google Sheets API using service account credentials.
Adheres to SRS FR-17 and LLD Section 6.4.
"""

import os
import logging
from pathlib import Path
from typing import Any, List, Optional
from intelligent_scraper.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Wrapper around gspread for Google Sheets API communication."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.client = None
        self.is_connected = False
        self._init_client()

    def _init_client(self) -> None:
        """Attempts authentication with gspread if credentials file exists."""
        creds_file = self.settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        if not creds_file or not Path(creds_file).exists():
            logger.info("Google Sheets credentials file not provided or does not exist. Operating in offline/local export mode.")
            return

        try:
            import gspread
            self.client = gspread.service_account(filename=creds_file)
            self.is_connected = True
            logger.info("Google Sheets client authenticated successfully.")
        except Exception as e:
            logger.warning(f"Failed to authenticate with Google Sheets API: {e}")
            self.is_connected = False

    def get_or_create_sheet(self, spreadsheet_id_or_title: str):
        """Opens existing sheet or raises error if offline."""
        if not self.is_connected or not self.client:
            return None

        try:
            # Try by key/id first
            return self.client.open_by_key(spreadsheet_id_or_title)
        except Exception:
            try:
                # Try by title
                return self.client.open(spreadsheet_id_or_title)
            except Exception as e:
                logger.error(f"Could not open spreadsheet: {e}")
                return None
