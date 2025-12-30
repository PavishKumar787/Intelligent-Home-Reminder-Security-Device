# backend/services/alert_store.py
# SINGLE SOURCE OF TRUTH for all alerts
# This file contains ONLY the shared list - do not define alerts anywhere else

from typing import List, Dict

alerts: List[Dict] = []
