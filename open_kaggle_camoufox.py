"""
Otvoriť Kaggle cez Camoufox browser
"""
from camoufox.sync_api import Camoufox
import time

print("Spúšťam Camoufox browser...")
print("Otváram Kaggle...")

with Camoufox(headless=False) as browser:
    # Otvor Kaggle
    page = browser.new_page()
    page.goto("https://www.kaggle.com/code")
    
    print("Kaggle otvorený!")
    print("Môžeš teraz manuálne nahrať notebook.")
    print("Stlač Enter keď skončíš...")
    
    input()
    
    print("Zatváram browser...")
