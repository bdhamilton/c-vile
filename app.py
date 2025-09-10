import random
from datetime import datetime
from flask import Flask, render_template, request, Response
import json
import os
import bleach
from functools import wraps

app = Flask(__name__)

# --------------------
# CONFIG
# --------------------

SUBMISSIONS_FILE = os.getenv('SUBMISSIONS_FILE', 'data/submissions.json')
GRIPES_FILE = os.getenv('GRIPES_FILE', 'data/gripes.json')

ADMIN_USER = os.getenv('ADMIN_USER', 'gripemaster')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'test')

# --------------------
# FILE PERSISTENCE
# --------------------

def load_gripes(filename = GRIPES_FILE):
    """Load JSON file, return empty list if file doesn't exist or is empty"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return []
    except (json.JSONDecodeError, FileNotFoundError):
        return ["No gripes."]

def save_gripes(data, filename = GRIPES_FILE):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# --------------------
# PUBLIC ROUTES
# --------------------

@app.route("/")
def gripe():
    return render_template('index.html')

@app.route("/random-gripe")
def get_a_gripe():
    gripes = load_gripes()
    return random.choice(list(gripes.values()))

@app.post("/submit-a-gripe")
def submit_a_gripe():
    gripe = request.headers.get('HX-Prompt')
    
    if gripe and gripe.strip():
        clean_gripe = bleach.clean(gripe.strip(), tags=[], strip=True)

        submission = {
            'text': clean_gripe,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }

        submissions = load_gripes(SUBMISSIONS_FILE)
        submissions.append(submission)
        save_gripes(submissions, SUBMISSIONS_FILE)

    return '<div id="gripe-alert">Thanks for griping.</div>'

# --------------------
# AUTHENTICATION
# --------------------

def check_auth(username, password):
    """Check if a username/password combination is valid"""
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    """Send a 401 response that enables basic auth"""
    return Response(
        'You really want to see all the gripes?\n'
        'You\'re going to have to log in.', 401,
        {'WWW-Authenticate': 'Basic realm="Admin Area"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --------------------
# ADMIN ROUTES
# --------------------

@app.get("/gripes")
@requires_auth
def admin_page():
    gripes = load_gripes(GRIPES_FILE)
    submissions = load_gripes(SUBMISSIONS_FILE)
    return render_template("admin.html", gripes=gripes, submissions=submissions)

