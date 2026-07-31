# Contributing to Dental AI

Thank you for your interest in contributing to Dental AI! This guide will help you get started with the development workflow.

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git** for version control
- Optional: **Docker** for containerized development

### 1. Fork & Clone

```bash
# Fork the repo on GitHub, then clone
git clone https://github.com/<your-username>/dental-ai.git
cd dental-ai

# Add the original repo as upstream
git remote add upstream https://github.com/ericecek-code/dental-ai-fin.git
```

### 2. Set Up the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Set Up the Frontend

```bash
cd frontend
npm install
```

### 4. Run the Application

Start both servers in separate terminals:

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://localhost:5173` in your browser.

---

## 🔧 Development Workflow

### Branch Naming

Use descriptive branch names with prefixes:

| Prefix | Use Case |
|--------|----------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code refactoring |
| `test/` | Adding or updating tests |
| `chore/` | Maintenance tasks |

Example: `feat/add-dicom-support`, `fix/confidence-slider-range`

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Formatting, semicolons, etc. (no code change)
- `refactor` — Code restructuring (no feature or fix)
- `test` — Adding or updating tests
- `chore` — Build process, dependencies, tooling

**Examples:**
```
feat(backend): add DICOM file support to analyzer
fix(frontend): correct confidence slider min/max range
docs: update README with API endpoint examples
refactor(detector): extract color map to config module
```

---

## 🎨 Code Style

### Python (Backend)

- **Formatter:** [Black](https://github.com/psf/black)
- **Linter:** [Ruff](https://github.com/astral-sh/ruff) (recommended)
- **Max line length:** 88 characters (Black default)
- **Type hints:** Required for all public functions

```bash
# Auto-format before committing
black backend/
ruff check backend/ --fix
```

**Key conventions:**
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Use UPPER_SNAKE_CASE for constants
- Import order: stdlib → third-party → local (separated by blank lines)
- Docstrings: Google style for all public functions

### TypeScript/React (Frontend)

- **Formatter:** [Prettier](https://prettier.io/)
- **Linter:** [ESLint](https://eslint.org/) (configured via Vite)
- **Style guide:** Airbnb React/TypeScript

```bash
# Auto-format before committing
cd frontend
npx prettier --write src/
npx eslint src/ --fix
```

**Key conventions:**
- Use `camelCase` for variables and functions
- Use `PascalCase` for components and types
- Prefer functional components with hooks
- Destructure props in function signatures
- Use named exports (not default exports for components)

### File Organization

- Keep components in `src/components/` with one component per file
- Utility functions go in `src/lib/`
- API types and schemas stay in `backend/app/models/`
- ML pipeline modules belong in `backend/app/ml/`

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Backend starts without errors (`uvicorn app.main:app`)
- [ ] `GET /health` returns `{"status": "healthy"}`
- [ ] `POST /analyze/` returns detections for a sample X-ray
- [ ] Frontend loads at `http://localhost:5173`
- [ ] Image upload triggers analysis and shows results
- [ ] Overlay image downloads correctly
- [ ] No console errors in browser developer tools

---

## 📝 Pull Request Process

### 1. Create Your Branch

```bash
git checkout main
git pull upstream main
git checkout -b feat/your-feature-name
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the code style guidelines above
- Add or update tests if applicable
- Update documentation if your change affects the API or user-facing features

### 3. Commit & Push

```bash
git add .
git commit -m "feat(scope): clear description of change"
git push origin feat/your-feature-name
```

### 4. Open a Pull Request

- Target the `main` branch
- Use a descriptive title following commit message format
- Fill out the PR description with:
  - **What** does this change?
  - **Why** is this change needed?
  - **How** was this tested?
  - **Screenshots** if UI changes are involved

### 5. Code Review

- A maintainer will review your PR
- Address any requested changes
- Once approved, your PR will be merged

---

## 🏥 Dental Domain Guidelines

### Label Translations

When adding UI text related to dental conditions, provide both English and Slovak labels:

```typescript
// In src/lib/labels.ts
export const CLASS_LABELS_SK: Record<string, string> = {
  'Caries': 'Kaz',
  'Crown': 'Korunka',
  'Filling': 'Plomba',
  // ... etc
};
```

### Severity Classification

Maintain the three-tier severity system:
- **Urgent** 🚨 — Requires immediate attention (Caries, Periapical Lesion)
- **Treat Soon** ⚠️ — Should be addressed within weeks (Impacted Tooth, Missing Teeth)
- **Watch** 👀 — Monitor over time (Crown, Filling, Implant)

### Color Consistency

Each detection class has a fixed color for overlays. When adding or modifying classes:

1. Define the color in `backend/app/ml/detector.py` (`COLOR_MAP`)
2. Ensure sufficient contrast against X-ray grayscale backgrounds
3. Test with both bright and dark X-ray images
4. Document the color choice in your PR description

---

## 🐛 Reporting Bugs

When filing an issue, include:

1. **Environment:** OS, Python version, Node version, browser
2. **Steps to reproduce:** Clear, numbered steps
3. **Expected behavior:** What should happen
4. **Actual behavior:** What actually happens
5. **Screenshots:** If applicable
6. **Sample X-ray:** If the issue is ML-related (anonymized please)

---

## 💡 Feature Requests

We welcome ideas! When suggesting a feature:

- Explain the **clinical use case** it would serve
- Describe the **user workflow** step by step
- Note any **similar features** in other dental AI tools
- Consider **model performance** implications

---

## ❓ Questions?

Open a [GitHub Discussion](https://github.com/ericecek-code/dental-ai-fin/discussions) for questions, ideas, or general feedback.

---

## 📜 Code of Conduct

Be respectful, constructive, and professional. We're building tools to help dental professionals — let's keep that mission at the center of every interaction.
