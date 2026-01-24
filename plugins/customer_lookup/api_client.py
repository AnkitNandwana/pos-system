import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class CustomerAPIClient:
    """Client for fetching customer data from external API"""
    
    def __init__(self, base_url: str, timeout: int = 5, retry_attempts: int = 2):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
    
    def fetch_customer(self, identifier: str) -> Optional[Dict]:
        """Fetch customer data from external API with retry logic"""
        url = f"{self.base_url}/{identifier}/"
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"[API] Fetching customer: {identifier} (attempt {attempt + 1}/{self.retry_attempts})")
                response = requests.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"[API] Success: {data.get('customer_id', 'N/A')}")
                    return data
                elif response.status_code == 404:
                    logger.warning(f"[API] Customer not found: {identifier}")
                    return None
                else:
                    logger.error(f"[API] Error {response.status_code}: {response.text}")
                    
            except requests.Timeout:
                logger.error(f"[API] Timeout on attempt {attempt + 1}")
            except requests.RequestException as e:
                logger.error(f"[API] Request failed: {e}")
        
        return None
