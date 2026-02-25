# AGENTS.md

## Cursor Cloud specific instructions

### Project overview
PetriDishSim is a Python FastAPI service that simulates fungal/microbial growth in petri dishes, with chemical diffusion, metabolic pathway modeling, enzyme kinetics, and image segmentation modules. Authored by Mycosoft.

### Dev environment
- **Python 3.11+** required (`pyproject.toml` specifies `^3.11`; VM has 3.12).
- **Poetry** manages dependencies. The virtualenv is created in-project at `.venv/`.
- Run `poetry install` from the workspace root to install/refresh all deps.

### Running the application
- **Dev server:** `poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`
- **API docs:** `http://localhost:8000/docs` (Swagger UI)
- **Health check:** `GET /health`
- **Simulation endpoint:** `POST /chemical/step` (see `api/main.py` for schema)

### Linting
No project-level lint config exists. Use `ruff check src/ api/` for basic lint validation.

### Testing
No automated test suite exists yet (no `tests/` directory or pytest config). Validate by:
1. Importing modules: `poetry run python -c "from chemical.diffusion import ChemicalField; ..."`
2. Running the API and hitting endpoints with curl or the Swagger UI.

### Build
`poetry build` produces an sdist and wheel in `dist/`.

### Known gotchas
- **Numba is optional at runtime.** The diffusion module gracefully falls back to NumPy if Numba is unavailable, but it is included as a dependency in `pyproject.toml`.
- **Segmentation requires an external ONNX model file** not included in the repo. The `segmentation.inference.segment_image()` function expects a model path at runtime.
- **No external services needed.** The project is entirely self-contained (no databases, caches, or message queues).
- **Species data** lives in `data/species/*.json` (16 organism config files).
