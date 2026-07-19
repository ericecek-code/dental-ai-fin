# DenteScope AI — Production Deploy na RunPod (default odporúčanie)

> **Prečo RunPod?** RTX 4090 EU region za **0,40 USD/hod** (community) alebo **0,69 USD/hod** (secure), API-token based deploy (autonómne: ja to viem spraviť), 30+ global regionov, jednoduché Docker image.

---

## 1. Predpoklady (ktoré treba raz)

| Čo | Kde získať |
|---|---|
| RunPod účet | https://runpod.io → Sign Up |
| **RUNPOD_API_KEY** | RunPod → Settings → API Keys → vytvor nový |
| Docker nainštalovaný lokálne | https://docker.com (potrebný len na **build**; ak chceš využiť cloud-build, nie) |
| Tvoj **DOCKER_HUB_USERNAME** | https://hub.docker.com → Sign Up (free) |
| Verejný SSH kľúč | `ssh-keygen -t ed25519` (voliteľné, len ak chceš SSH prístup do Pod-u) |

> ⚠️ **`RUNPOD_API_KEY` daj len mne priamo v chate alebo ulož do `.env` v projekte** — nie do git repozitára, nie do pamäte agenta (ja si ho vytiahnem z `.env` keď budem robiť deploy).

---

## 2. Čo viem urobiť JA (autonómne) keď dostaneš token

Postupnosť krokov — **ja to celé viem spraviť za teba**:

### Krok A — Priprav image (5 min)

```bash
cd C:/Users/PC1/Desktop/dental-ai
docker build -t $DOCKER_HUB_USERNAME/dental-ai:latest .
docker push $DOCKER_HUB_USERNAME/dental-ai:latest
```

Výsledok: verejný image so FastAPI backendom + YOLOv8x-seg modelom (~3 GB Docker image).

### Krok B — Vytvor RunPod Pod cez API token (1 min)

```bash
# RunPod CLI nainstaluj raz
pip install runpodctl

# Nastav token (daj ho do .env v repo — nie do command line!)
runpodctl config --apiKey $RUNPOD_API_KEY

# Vytvor persistentny pod
runpodctl create pod \
  --name "dental-ai-prod" \
  --imageName "$DOCKER_HUB_USERNAME/dental-ai:latest" \
  --gpuType "NVIDIA GeForce RTX 4090" \
  --gpuCount 1 \
  --containerDiskSize 20 \
  --volumeSize 50 \
  --ports "8000/http" \
  --env "PUBLIC_URL=https://dental-ai-prod-8000.proxy.runpod.net" \
  --startScript "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"
```

Výstup: verejná URL typu `https://dental-ai-prod-<id>.proxy.runpod.net` + endpoint typu `https://api.runpod.ai/v2/<pod-id>/runsync` (pre asynchrónne inference).

### Krok C — Health-check + auto-restart watchdog (1 min)

```bash
*/5 * * * * curl -sf -m 4 https://dental-ai-prod-<id>.proxy.runpod.net/health \
  || runpodctl restart pod dental-ai-prod
```

Toto sa dá vložiť do `cron` (na tvojom PC) alebo ako samostatný **Hermes watchdog** čo vieš nastaviť cez mňa.

### Krok D — HTTPS + custom doména (voliteľné, 10 min)

Ak chceš `api.dentescope.ai` namiesto runpod.net:

1. CNAME `api.dentescope.ai` → `dental-ai-prod-<id>.proxy.runpod.net` (v tvojom DNS)
2. RunPod auto-terminuje HTTPS na runpod.net
3. Cloudflare proxy pridať → 100% free + auto-DDoS ochrana

---

## 3. Mesačná kalkulácia (3 režimy)

| Režim | GPU | Hodín/mesiac | ~Cena |
|---|---|---|---|
| **Background only** (1 task/deň, 8h ráno) | RTX 4090 community | 240 | **96 USD/mes** |
| **Practice hours** (8–18 h, 5 dní) | RTX 4090 secure | 350 | **241 USD/mes** |
| **24/7 listen** (vždy-on, kliniky) | RTX 4090 secure | 720 | **497 USD/mes** |
| **Burst only** (auto-stop po 5 min idle) | RTX 4090 secure | ~30 | **21 USD/mes** |

> 💡 **Burst only** je najúspornejší pre nízku záťaž — RunPod Pod sa dá nastaviť na **auto-stop po X minútach nečinnosti**.

---

## 4. API token — kde ho uložiť

### ✅ Bezpečnostne správne:

1. **Pridaj `RUNPOD_API_KEY` do `C:/Users/PC1/Desktop/dental-ai/.env`** (tento súbor je v `.gitignore`)
2. **Daj mi vedieť** že je tam — ja si ho prečítam pred deploy, ale neukladám ho do pamäte

### ❌ Nikde inam:

- ❌ Nie do git
- ❌ Nie na verejnú URL
- ❌ Nie do chat-u (akekoľvek lepšie ako na server, ale najlepšie cez .env)
- ❌ Nie do mňa (do pamäte agentov — ani mojej)

---

## 5. Overenie či deploy funguje

```bash
# Health check
curl -s https://dental-ai-prod-<id>.proxy.runpod.net/health
# Ocakavane: {"status":"healthy"}

# Skuska analyzy
curl -s -X POST "https://dental-ai-prod-<id>.proxy.runpod.net/analyze/?conf=0.05" \
  -F "file=@test_images/caries_1.jpg" \
  | head -30
# Ocakavane: JSON s detection_count: 76 a quadrantami Q1-Q4
```

Ak oba fungujú → deploy úspešný.

---

## 6. Alternatívy (ak by si nechcel RunPod)

| Platforma | Prečo | Cena | API token |
|---|---|---|---|
| **DigitalOcean Droplet GPU** | flat-rate, stabilné | 0,76 USD/hod = ~550 USD/mes (24/7) | ✅ |
| **Modal.com** | auto-cold-start, pay-as-you-go | ~30 USD/mes pri 20 analýz/deň | ✅ |
| **HuggingFace Endpoints** | managed, image-based | 0,60 USD/hod always-on | ✅ |
| **Vast.ai** | najlacnejšie, marketplace | 0,30 USD/hod RTX 3090 | ⚠️ menej spoľahlivé |

Viac porovnaní: prečítaj si `deploy/COMPARISON.md`.

---

## 7. Ja (Hermes) — čo potrebujem na odoslanie deploy

Povedz mi:

1. **„Choď na RunPod"** — ja idem, **ak mi dáš `RUNPOD_API_KEY` do `dental-ai/.env`** (alebo mi ho pošli priamo — ale pozor, ostane v chate)
2. **„Choď na DigitalOcean / Modal"** — analogicky potrebujem `DO_TOKEN` / `MODAL_TOKEN_ID+SECRET`
3. **„Priprav len konfigy"** — nechám ťa to nasadiť manuálne (pripravený Dockerfile + návod)

Vyber 1-3 alebo inú možnosť.
