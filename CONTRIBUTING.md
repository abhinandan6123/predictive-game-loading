# Contributing to PulseLoad

Thank you for your interest in contributing to PulseLoad.

PulseLoad is a research-engineering and hackathon prototype focused on predictive adaptive game loading. Contributions that improve correctness, observability, reproducibility, performance evaluation, safety, and maintainability are welcome.

## Development Setup

### Prerequisites

- Python 3.12
- Git
- Docker (optional, for container validation)

### Clone the Repository

```bash
git clone https://github.com/abhinandan6123/predictive-game-loading.git
cd predictive-game-loading
```

### Create and Activate a Virtual Environment

**Git Bash on Windows:**

```bash
python -m venv .venv
source .venv/Scripts/activate
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

Start the API locally:

```bash
uvicorn services.api.main:app --reload
```

The local API is available at `http://127.0.0.1:8000`.

Useful endpoints include:

- `/health` — application health status
- `/docs` — interactive API documentation
- `/metrics` — runtime metrics
- `/dashboard` — PulseLoad runtime dashboard

## Quality Checks

Before opening a pull request, run:

```bash
python -m ruff check .
python -m ruff format --check .
pytest -q
git diff --check
```

The project CI workflow also validates these checks and performs a Docker build.

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

## Contribution Workflow

1. Start from the latest `develop` branch.
2. Create a focused branch for your change.
3. Keep commits small and descriptive.
4. Add or update tests when behavior changes.
5. Run the quality checks locally.
6. Open a pull request against `develop`.
7. Address review feedback before merging.

Example:

```bash
git switch develop
git pull origin develop
git switch -c feature/your-change
```

## Pull Request Guidelines

Please include:

- A clear description of the change
- The motivation or problem being addressed
- Relevant testing evidence
- Any performance or behavior impact
- Documentation updates when needed

## Code Quality Principles

- Prefer clear, maintainable implementations.
- Keep prediction and policy decisions observable.
- Preserve deterministic behavior where possible.
- Avoid introducing hidden side effects.
- Treat performance claims as evidence-backed measurements.
- Keep responsible-play constraints enforced independently of optimization goals.

## Reporting Issues

When reporting a bug, include the environment, Python version, reproduction steps, expected behavior, actual behavior, and relevant logs when available.

## License

By contributing to this repository, you agree that your contributions will be licensed under the project MIT License.
