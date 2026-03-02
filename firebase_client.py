"""
Firebase Firestore client for state management and real-time data streaming.
Implements robust error handling, connection pooling, and automatic reconnection.
"""
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import time
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core.exceptions import GoogleAPICallError, RetryError

from config import config

class FirebaseClient:
    """Firebase Firestore client with connection management and error handling"""
    
    def __init__(self):
        self.client: Optional[FirestoreClient] = None
        self.app = None
        self.connected = False
        self.last_connection_attempt = None
        self.executor = ThreadPoolExecutor(max