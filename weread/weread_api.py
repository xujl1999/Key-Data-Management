import requests
import json
import time
import os
from pathlib import Path

class WereadAPI:
    BASE_URL = "https://weread.qq.com"
    
    def __init__(self, cookies: dict = None, cookie_str: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json"
        })
        
        if cookies:
            self.session.cookies.update(cookies)
        if cookie_str:
            # Parse cookie string manually if provided
            for cookie in cookie_str.split(';'):
                if '=' in cookie:
                    k, v = cookie.strip().split('=', 1)
                    self.session.cookies.set(k, v, domain=".weread.qq.com")

    def check_login(self):
        """Verify login status by checking for specific cookie fields"""
        # Typically looking for wr_vid and wr_skey
        cookies = self.session.cookies.get_dict()
        if 'wr_vid' not in cookies or 'wr_skey' not in cookies:
             # Try refreshing?
             return False
        return True

    def get_notebooks(self):
        """Get list of books with notes"""
        url = f"{self.BASE_URL}/api/user/notebook"
        # From plugin: /api/user/notebook
        try:
            resp = self.session.get(url)
            if resp.status_code == 401:
                print("Cookie expired.")
                return []
            data = resp.json()
            # Plugin says resp.json.books
            return data.get("books", [])
        except Exception as e:
            print(f"Error fetching notebooks: {e}")
            return []

    def get_book_detail(self, book_id):
        """Get book metadata"""
        url = f"{self.BASE_URL}/web/book/info"
        params = {"bookId": book_id}
        try:
            resp = self.session.get(url, params=params)
            return resp.json()
        except Exception as e:
            print(f"Error fetching book detail for {book_id}: {e}")
            return None

    def get_highlights(self, book_id):
        """Get bookmarks/highlights"""
        url = f"{self.BASE_URL}/web/book/bookmarklist"
        params = {"bookId": book_id}
        try:
            resp = self.session.get(url, params=params)
            return resp.json()
        except Exception as e:
            print(f"Error fetching highlights for {book_id}: {e}")
            return None

    def get_reviews(self, book_id):
        """Get reviews/thoughts"""
        url = f"{self.BASE_URL}/web/review/list"
        params = {
            "bookId": book_id,
            "listType": 11,
            "mine": 1,
            "synckey": 0
        }
        try:
            resp = self.session.get(url, params=params)
            return resp.json()
        except Exception as e:
            print(f"Error fetching reviews for {book_id}: {e}")
            return None
            
    def get_chapters(self, book_id):
        """Get chapter info"""
        url = f"{self.BASE_URL}/web/book/chapterInfos"
        payload = {"bookIds": [book_id]}
        try:
            resp = self.session.post(url, json=payload)
            return resp.json()
        except Exception as e:
            print(f"Error fetching chapters for {book_id}: {e}")
            return None

    def get_progress(self, book_id):
        """Get reading progress and time"""
        url = f"{self.BASE_URL}/web/book/getProgress"
        params = {"bookId": book_id}
        try:
            resp = self.session.get(url, params=params)
            return resp.json()
        except Exception as e:
            print(f"Error fetching progress for {book_id}: {e}")
            return None
