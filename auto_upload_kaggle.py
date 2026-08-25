"""
Automatický upload notebooku na Kaggle cez Playwright
"""
from playwright.sync_api import sync_playwright
import time
import json

# Načítaj credentials
with open(r'C:\Users\PC1\.kaggle\kaggle.json', 'r') as f:
    creds = json.load(f)

username = creds['username']
password = creds['key']  # Toto je API key, nie heslo

print("=" * 60)
print("DENTAL AI - AUTO UPLOAD NA KAGGLE")
print("=" * 60)

with sync_playwright() as p:
    # Spusti browser
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 1. Otvor Kaggle
    print("\n1. Otváram Kaggle...")
    page.goto("https://www.kaggle.com/account/login")
    time.sleep(3)
    
    # 2. Prihlás sa
    print("2. Prihlasujem sa...")
    
    # Klikni na "Sign in with email"
    try:
        page.click('text=Sign in with email', timeout=10000)
        time.sleep(2)
    except:
        print("   Zadaj email manuálne...")
    
    # Zadaj email
    try:
        page.fill('input[name="email"]', f'{username}@gmail.com')
        time.sleep(1)
        page.click('button[type="submit"]')
        time.sleep(2)
    except:
        print("   Zadaj email/heslo manuálne v browseri")
        print("   Stlač Enter keď sa prihlásiš...")
        input()
    
    # 3. Otvor nový notebook
    print("3. Otváram nový notebook...")
    page.goto("https://www.kaggle.com/code")
    time.sleep(3)
    
    # Klikni "New Notebook"
    try:
        page.click('text=New Notebook', timeout=10000)
        time.sleep(5)
    except:
        print("   Vytvor nový notebook manuálne")
        print("   Stlač Enter keď si v editore...")
        input()
    
    # 4. Nahraj notebook
    print("4. Nahrávam notebook...")
    print("   Skopíruj obsah z: C:\\Users\\PC1\\Desktop\\dental-ai\\kaggle_training.ipynb")
    print("   Stlač Enter keď si skopíroval...")
    input()
    
    # 5. Nastav GPU
    print("5. Nastav GPU P100 v Settings...")
    print("   Stlač Enter keď si nastavil...")
    input()
    
    # 6. Pridaj dataset
    print("6. Pridaj dataset: eriksmite/dental-mega-dataset")
    print("   Stlač Enter keď si pridal...")
    input()
    
    # 7. Spusti
    print("7. Klikni Run All!")
    print("   Tréning bude trvať ~7-8 hodín")
    
    print("\n" + "=" * 60)
    print("HOTOVO! Sleduj priebeh na Kaggle.")
    print("=" * 60)
    
    # Nechaj browser otvorený
    print("\nStlač Enter pre zatvorenie...")
    input()
    
    browser.close()
