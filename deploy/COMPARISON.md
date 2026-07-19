# DenteScope AI — Hostingové platformy: porovnanie

> Ceny sú **orientačné** (rok 2025–2026), overené z oficiálnych stránok. Pre presnú aktuálnu cenu treba ísť priamo na pricing stránku platformy.

## Porovnanie (pre RTX 4090 tier **alebo** ekvivalent)

| | **RunPod Pods** | **DigitalOcean Droplets GPU** | **Modal.com** | **HuggingFace Endpoints** |
|---|---|---|---|---|
| **Cena / hod (GPU)** | $0.40–$0.69 (community/secure) | $0.76 (flat monthly: $550/24×7) | $1.37/h A10G (cold + warm) | $0.60/h always-on |
| **GPU ekvivalent** | RTX 4090 / A100 / H100 | RTX 4000 Ada | A10G / T4 (serverless) | A10G / A100 |
| **Cena 8 h/deň 30 dní (24h zákazník)** | $96–$166/mes | $182/mes | $30–$60/mes (low traffic) | $144/mes |
| **Cena 24/7** | $288–$497/mes | $550/mes | burst-limitovaný | $432/mes |
| **EU regiony** | ✅ Frankfurt, Amsterdam, Madrid, Stockholm | ✅ Frankfurt, Amsterdam | ✅ EU-west | ⚠️ US primárne |
| **Docker image** | ✅ ľubovoľný | ✅ (ale žiadny GPU image upload) | ✅ `modal.Image` | ✅ Docker alebo HF Spaces |
| **API token deploy** | ✅ `RUNPOD_API_KEY` cez `runpodctl` | ✅ `DIGITALOCEAN_TOKEN` cez `doctl` | ✅ `MODAL_TOKEN_ID+SECRET` | ✅ `HF_TOKEN` |
| **Auto-scale** | nie (Pod = fixed) | nie (droplet = fixed) | ✅ auto cold/warm | ✅ auto |
| **Persistentný disk** | ✅ volume 50+ GB | ✅ volume | ✅ volumes | ⚠️ obmedzené |
| **Cold start** | ~2–5 s (model load) | ~10 s | ~2–5 s | variabilné |
| **HTTPS terminácia** | ✅ runpod.net subdoména | ✅ vlastná IP + Cloudflare | ✅ vlastná | ✅ vlastná |
| **Vlastná doména** | ✅ cez CNAME | ✅ | ✅ | ✅ |
| **Support** | community (Discord) | paid support | paid (community + paid) | free+paid |

---

## Rozhodovacia matrica (pre tvoj use-case)

### Ak prevádzkuješ **kliniku / ambulanciu**:
- 🏆 **RunPod Secure Cloud**, RTX 4090, **21 USD/mes pri auto-burst** (5 min idle režim)
- 🏆 Alebo **DO Droplets GPU flat** ak chceš **stále rovnaký mesačný účet**

### Ak robíš **výskum / neprodukcia / zriedkavé testovanie**:
- 🏆 **Modal.com** — pay-as-you-go, ~30–60 USD/mes, bez starostí
- 🏆 Alebo **RunPod Community Cloud** — lacnejšie ($0.40/h) alebo Secure ($0.69/h)

### Ak chceš **managed (žiadny Docker, žiadne GPU)**:
- 🏆 **HuggingFace Inference Endpoints** — image-based, jednoducho nasadíš cez UI
- ⚠️ Ale CRITICAL: niektoré regióny sú mimo EU — over si

### Ak chceš **úplne najlacnejšie (ale riskantnejšie)**:
- ⚠️ **Vast.ai** (marketplace) — lacnejšie ako RunPod ale menej stabilné
- ⚠️ cold-starts, provider sa môže zmeniť

---

## Bezpečnostné odporúčania (pre všetky platformy)

1. **API kľúče** — vždy `.env` v repo, **nie** do gitu, **nie** v CLI history
2. **HTTPS terminácia** — RunPod/DO/Modal ju poskytujú; **vždy** cez HTTPS, nikdy plain HTTP
3. **CORS** — povoľ len produkčný frontend origin (napr. `https://app.dentescope.ai`), počas vývoja aj `localhost:5173`
4. **API token** — backend by mal mať **autentifikáciu** (header `Authorization: Bearer <token>`) ak nie je verejný
5. **Rate limiting** — backend by mal mať `slowapi` alebo ekvivalent (odporúčam doplniť do FastAPI v ďalšom kroku)
6. **Monitoring** — UptimeRobot free tier (https://uptimerobot.com) kontroluje `/health` každých 5 min

---

## Čo odporúčam TERAZ (default)

**RunPod Pods — RTX 4090, community tier, s auto-burst.**

- Najlacnejší
- Najjednoduchší API-token deploy (ja to viem spraviť)
- EU region
- Najrýchlejší cold-start pre YOLOv8 (model sa zmestí do 24 GB VRAM)

Tvoj ďalší krok: **povedz „Choď na RunPod" + daj mi RUNPOD_API_KEY cez `.env` v `dental-ai/`** a ja spravím celý deploy autonómne.

---

## Súvisiace dokumenty

- `deploy_runpod.md` — konkrétny návod ako nasadiť (build, push, create pod, watchdog)
- `docker-compose.yml` — lokálne testovanie production image
- `Dockerfile` (root projektu) — definícia image
- `.env.example` — env variables kde dáš tokeny
