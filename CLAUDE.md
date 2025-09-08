# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

C-VILE is a Flask web application for collecting and displaying user-submitted "gripes" (complaints). It uses HTMX for interactive frontend behavior without JavaScript frameworks.

## Architecture

- **app.py**: Main Flask application containing all routes and business logic
- **templates/**: Jinja2 HTML templates
  - `index.html`: Main public interface with HTMX interactions
  - `admin.html`: Admin interface for viewing gripes
  - `_gripe_list.html`: Partial template component
- **static/style.css**: CSS styling
- **submissions.json**: User submission storage (JSON file)
- **gripes.json**: Approved gripes storage (JSON file, created when needed)

## Development Setup

The project uses Python 3.13 with a virtual environment:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (Flask, bleach)
pip install flask bleach

# Run development server
python app.py
```

## Key Technical Details

- **Data Persistence**: JSON file-based storage (no database)
- **Security**: Uses `bleach` library to sanitize user input
- **Frontend**: HTMX for dynamic interactions, no JavaScript framework
- **Admin Access**: Hardcoded credentials in `app.py` (ADMIN_USER/ADMIN_PASS)

## Routes

- `GET /`: Main gripe display page
- `GET /random-gripe`: Returns random gripe text
- `POST /submit-a-gripe`: Accepts gripe submissions via HTMX prompt
- `GET /gripes`: Admin page for viewing all gripes

## Data Flow

1. Public users view random gripes and can submit new ones
2. Submissions are stored in `submissions.json` with "pending" status
3. Admin can view submissions through `/gripes` endpoint
4. Approved gripes are meant to be moved to the main gripes list in `app.py`