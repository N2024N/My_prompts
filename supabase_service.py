"""
Supabase Service using requests library instead of supabase-py
to avoid compatibility issues.
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    """Simple Supabase client using direct REST API calls"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase service.
        
        Args:
            url: Supabase project URL (e.g., https://your-project.supabase.co)
            key: Service Role Key (sb_secret_...)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url:
            raise ValueError("SUPABASE_URL is required")
        if not self.key:
            raise ValueError("SUPABASE_KEY is required")
            
        # Clean up URL
        if not self.url.startswith("http"):
            self.url = f"https://{self.url}"
        if self.url.endswith("/"):
            self.url = self.url[:-1]
            
        # Headers for all requests
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Cache for table URLs
        self._table_urls = {}
        
        logger.info(f"Supabase service initialized for {self.url[:30]}...")
        
    def _get_table_url(self, table_name: str) -> str:
        """Get REST URL for a table"""
        if table_name not in self._table_urls:
            self._table_urls[table_name] = f"{self.url}/rest/v1/{table_name}"
        return self._table_urls[table_name]
    
    def test_connection(self) -> bool:
        """Test if we can connect to Supabase"""
        try:
            # Try to list tables or get a simple response
            response = requests.get(
                f"{self.url}/rest/v1/",
                headers={"apikey": self.key}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def create_activation_code(self, code: str, email: str = "", 
                              plan: str = "standard",
                              is_used: bool = False) -> Dict[str, Any]:
        """
        Create a new activation code in the database.
        
        Args:
            code: The activation code string
            email: Optional email for tracking
            plan: License plan (standard, pro, team)
            is_used: Whether the code is already used
            
        Returns:
            Created record
        """
        table_url = self._get_table_url("activation_codes")
        
        # Map to actual table column names
        data = {
            "activation_code": code,
            "email": email,
            "status": "used" if is_used else "unused",
            "plan": plan,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
            
        try:
            response = requests.post(
                table_url,
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                logger.info(f"Created activation code: {code[:8]}... (plan: {plan})")
                return response.json()[0] if isinstance(response.json(), list) else response.json()
            else:
                logger.error(f"Failed to create activation code: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}
                
        except Exception as e:
            logger.exception(f"Error creating activation code: {e}")
            return {"error": str(e)}
    
    def validate_activation_code(self, code: str) -> Dict[str, Any]:
        """
        Validate an activation code.
        
        Args:
            code: The activation code to validate
            
        Returns:
            Validation result with code details if valid
        """
        table_url = self._get_table_url("activation_codes")
        
        # Query by activation_code column (not "code")
        params = {
            "activation_code": f"eq.{code}",
            "select": "*"
        }
        
        try:
            response = requests.get(
                table_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                records = response.json()
                if records and len(records) > 0:
                    record = records[0]
                    
                    # Check if code is already used (check status field)
                    if record.get("status") == "used":
                        return {
                            "valid": False,
                            "message": "Activation code has already been used",
                            "code": code
                        }
                    
                    # Check if revoked
                    if record.get("status") == "revoked":
                        return {
                            "valid": False,
                            "message": "Activation code has been revoked",
                            "code": code
                        }
                    
                    # Note: No expiration mechanism in current schema
                    # If expiration is needed, add expires_at column to table
                    pass
                    
                    # Code is valid
                    return {
                        "valid": True,
                        "message": "Activation code is valid",
                        "code": code,
                        "record": record
                    }
                else:
                    return {
                        "valid": False,
                        "message": "Activation code not found",
                        "code": code
                    }
            else:
                logger.error(f"Error validating activation code: {response.status_code} - {response.text}")
                return {
                    "valid": False,
                    "message": f"Database error: {response.status_code}",
                    "code": code
                }
                
        except Exception as e:
            logger.exception(f"Exception validating activation code: {e}")
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}",
                "code": code
            }
    
    def mark_activation_code_used(self, code: str, notion_page_id: str = "") -> Dict[str, Any]:
        """
        Mark an activation code as used.
        
        Args:
            code: The activation code to mark as used
            notion_page_id: Optional Notion page ID for tracking
            
        Returns:
            Update result
        """
        table_url = self._get_table_url("activation_codes")
        
        # First, get the record to update (query by activation_code column)
        params = {"activation_code": f"eq.{code}", "select": "id,status"}
        response = requests.get(table_url, headers=self.headers, params=params)
        
        if response.status_code != 200 or not response.json():
            return {
                "success": False,
                "message": "Activation code not found",
                "code": code
            }
        
        record = response.json()[0]
        record_id = record.get("id")
        
        # Check if already used
        if record.get("status") == "used":
            return {
                "success": False,
                "message": "Activation code has already been used",
                "code": code
            }
        
        # Update the record (set status to 'used' and add used_at timestamp)
        update_data = {
            "status": "used",
            "used_at": datetime.utcnow().isoformat() + "Z"
        }
        
        if notion_page_id:
            update_data["notion_page_id"] = notion_page_id
        
        try:
            update_url = f"{table_url}?id=eq.{record_id}"
            update_response = requests.patch(
                update_url,
                headers=self.headers,
                json=update_data
            )
            
            if update_response.status_code == 204 or update_response.status_code == 200:
                logger.info(f"Marked activation code as used: {code[:8]}...")
                return {
                    "success": True,
                    "message": "Activation code marked as used",
                    "code": code
                }
            else:
                logger.error(f"Failed to mark activation code as used: {update_response.status_code} - {update_response.text}")
                return {
                    "success": False,
                    "message": f"Update failed: {update_response.status_code}",
                    "code": code
                }
                
        except Exception as e:
            logger.exception(f"Error marking activation code as used: {e}")
            return {
                "success": False,
                "message": f"Update error: {str(e)}",
                "code": code
            }
    
    def get_activation_code_stats(self) -> Dict[str, Any]:
        """
        Get statistics about activation codes.
        
        Returns:
            Statistics including total codes, used, available, etc.
        """
        table_url = self._get_table_url("activation_codes")
        
        try:
            # Get all records (use correct column names based on actual table schema)
            response = requests.get(
                table_url,
                headers=self.headers,
                params={"select": "id,activation_code,status,created_at,used_at,plan,email,notion_page_id,metadata"}
            )
            
            if response.status_code == 200:
                records = response.json()
                
                total = len(records)
                used = sum(1 for r in records if r.get("status") == "used")
                available = total - used
                revoked = sum(1 for r in records if r.get("status") == "revoked")
                
                # Count by plan
                plan_counts = {}
                for r in records:
                    plan = r.get("plan", "unknown")
                    plan_counts[plan] = plan_counts.get(plan, 0) + 1
                
                return {
                    "total_codes": total,
                    "used_codes": used,
                    "available_codes": available,
                    "revoked_codes": revoked,
                    "plan_distribution": plan_counts,
                    "records": records[:10]  # Limit records in response for performance
                }
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "total_codes": 0,
                    "used_codes": 0,
                    "available_codes": 0,
                    "revoked_codes": 0,
                    "plan_distribution": {}
                }
                
        except Exception as e:
            logger.exception(f"Error getting activation code stats: {e}")
            return {
                "error": str(e),
                "total_codes": 0,
                "used_codes": 0,
                "available_codes": 0,
                "revoked_codes": 0,
                "plan_distribution": {}
            }

# Singleton instance
supabase_service = None

def get_supabase_service() -> SupabaseService:
    """Get or create the Supabase service instance"""
    global supabase_service
    if supabase_service is None:
        supabase_service = SupabaseService()
    return supabase_service