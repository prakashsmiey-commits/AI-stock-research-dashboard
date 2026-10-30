import requests
import pandas as pd
import streamlit as st
import time

# NSE Session Helper for Streamlit
class StreamlitNSESession:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/option-chain",
        }
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        # Warm cookies
        try:
            self.s.get("https://www.nseindia.com", timeout=5)
            self.s.get("https://www.nseindia.com/option-chain", timeout=5)
        except:
            pass

    def get_option_chain(self, symbol="NIFTY"):
        is_index = symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
        url = f"https://www.nseindia.com/api/option-chain-{'indices' if is_index else 'equities'}?symbol={symbol}"
        try:
            r = self.s.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
        except:
            # Re-warm session on failure
            try:
                self.s = requests.Session()
                self.s.headers.update(self.headers)
                self.s.get("https://www.nseindia.com/option-chain", timeout=5)
                r = self.s.get(url, timeout=10)
                if r.status_code == 200:
                    return r.json()
            except:
                pass
        return None
