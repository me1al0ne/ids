import time
import random
from tiktok_client import TikTokClient
from config import ACCOUNTS

class AccountManager:
    def __init__(self):
        self.accounts = []
        self._load_accounts()
    
    def _load_accounts(self):
        """Load accounts from config"""
        for name, creds in ACCOUNTS.items():
            self.accounts.append({
                "name": name,
                "client": TikTokClient(creds),
                "last_used": 0,
                "share_count": 0
            })
    
    def get_account(self):
        """Get an available account with rate limiting"""
        # Sort accounts by last used time
        self.accounts.sort(key=lambda x: x["last_used"])
        
        # Check rate limits (max 1 share per minute per account)
        account = self.accounts[0]
        if time.time() - account["last_used"] < 60:
            time.sleep(60 - (time.time() - account["last_used"]))
        
        # Update account usage
        account["last_used"] = time.time()
        account["share_count"] += 1
        
        return account
    
    def share_video(self, video_url):
        """Share a video using an available account"""
        account = self.get_account()
        success, message = account["client"].share_video(video_url)
        return {
            "account": account["name"],
            "success": success,
            "message": message
        }
