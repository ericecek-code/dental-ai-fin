# Dental AI - Projekt pre agenta Mimo

## Zadanie: Stiahnuť a pripraviť DENTEX dataset

### Cieľ
Stiahnuť dataset `ibrahimhamamci/DENTEX` z Hugging Face do priečinka `datasets/dentex/`, rozbaliť archívy a pripraviť ho v YOLO formáte.

### Pracovný priecin
```
C:\Users\PC1\Desktop\dental-ai\datasets\dentex
```

### Kroky
1. **Stiahnuť dataset**
   ```python
   from huggingface_hub import snapshot_download
   snapshot_download(
       repo_id='ibrahimhamamci/DENTEX',
       repo_type='dataset',
       local_dir='datasets/dentex'
   )
   ```

2. **Rozbaliť archívy**
   - Rozbaliť všetky `.zip` súbory v `datasets/dentex/DENTEX/`
   - `test_data.zip`, `validation_data.zip`, `training_data.zip`

3. **Skontrolovať obsah**
   - Prečítať `README.md` z datasetu
   - Skontrolovať `validation_triple.json` pre formát anotácií
   - Zistiť štruktúru tried

4. **Vytvoriť YOLO konfiguráciu**
   - Vytvoriť `datasets/dentex/data.yaml` s:
     - `path:` ukazovateľ na dátový priečin
     - `train:` a `val:` cesty
     - `names:` zoznam tried

### Dôležité
- Nepoužívaj `python3.11` — pracuješ v environment `python3.12`
- Nepushuj dataset súbory na GitHub (ako pravidlá Git LFS)
- Commituj iba konfiguračné súbory (`*.yaml`, `README.md`, malé JSON)
- Ak je súbor väčší ako 100MB, nevoľ `git add`

### Komunikácia
- Ak potrebuješ prístupové tokeny, použi environment variable `HF_TOKEN`
- Loguj pokrok každú minútu pre dlhé operácie
- Ak nastane error, zastav a označ ako `BLOCKED`

## Spojenie pre pracovnú skupinu

### Diskusia
- Toto je pracovný priecin pre projekt Dental AI
- Všetci členi tímu môžu tu nechávať správy, ktoré sa objavia ako `messages.md`
- Použij `status.yaml` pre sledovanie stavu úlohy

### Status kľúč
- 🟢 `ready` - pripravené na štart
- 🟡 `in_progress` - pracujem na tom
- 🔴 `blocked` - potrebujem pomoc
- ✅ `completed` - dokončené
