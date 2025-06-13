import requests
import random
import json
from config import TIKTOK_API_HOST, TIKTOK_SHARE_ENDPOINT, PROXIES

class TikTokClient:
    def __init__(self, account):
        self.account = account
        self.headers = self._get_headers()
    
    def _get_headers(self):
        """Generate TikTok API headers"""
        return {
            "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 11; en_US; Pixel 4; Build/RQ3A.211001.001; Cronet/58.0.2991.0)",
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip",
            "Connection": "keep-alive",
            "X-SS-DP": "1233",
            "X-Tt-Token": self.account["session_id"],
            "X-Gorgon": self._generate_x_gorgon(),
            "X-Khronos": str(int(time.time()))
        }
    
    def _generate_x_gorgon(self):
        """Generate X-Gorgon header (simplified version)"""
        # In a real implementation, this would be a complex algorithm
        return "".join(random.choices("0123456789abcdef", k=32))
    
    def _get_proxy(self):
        """Get a random proxy"""
        return {"https": random.choice(PROXIES)} if PROXIES else None
    
    def share_video(self, video_url):
        """Share a TikTok video"""
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(video_url)
            if not video_id:
                return False, "Invalid TikTok URL"
            
            # Prepare request payload
            payload = {
                "aweme_id": video_id,
                "share_to": "copy",  # Options: copy, more, whatsapp, etc.
                "type": 1,
                "channel_list": "[]"
            }
            
            # Make API request
            response = requests.post(
                f"{TIKTOK_API_HOST}{TIKTOK_SHARE_ENDPOINT}",
                headers=self.headers,
                data=payload,
                proxies=self._get_proxy(),
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                return True, "Shared successfully"
            else:
                return False, f"API error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, str(e)
    
    def _extract_video_id(self, url):
        """Extract video ID from TikTok URL"""
        # Example: https://www.tiktok.com/@user/video/1234567890123456789
        parts = url.split("/")
        if len(parts) >= 6 and parts[5].startswith("video"):
            return parts[6]
        return None
