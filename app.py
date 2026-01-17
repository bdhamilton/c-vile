import random
import string
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

@app.delete("/admin/submissions/<int:submission_index>")
@requires_auth
def delete_submission(submission_index):
    submissions = load_gripes(SUBMISSIONS_FILE)

    if 0 <= submission_index < len(submissions):
        del submissions[submission_index]
        save_gripes(submissions, SUBMISSIONS_FILE)

    # Return updated submissions list partial
    return render_template("_submissions_list.html", submissions=submissions)


def generate_gripe_id(existing_ids, length=6):
    """Generate a unique alphanumeric ID for a gripe"""
    chars = string.ascii_lowercase + string.digits
    while True:
        new_id = ''.join(random.choice(chars) for _ in range(length))
        if new_id not in existing_ids:
            return new_id


@app.post("/admin/gripes")
@requires_auth
def add_gripe():
    gripe_text = request.form.get('gripe', '').strip()

    if gripe_text:
        clean_gripe = bleach.clean(gripe_text, tags=[], strip=True)
        gripes = load_gripes(GRIPES_FILE)

        new_id = generate_gripe_id(gripes.keys())
        gripes[new_id] = clean_gripe
        save_gripes(gripes, GRIPES_FILE)
    else:
        gripes = load_gripes(GRIPES_FILE)

    return render_template("_gripes_list.html", gripes=gripes)


@app.delete("/admin/gripes/<gripe_id>")
@requires_auth
def delete_gripe(gripe_id):
    gripes = load_gripes(GRIPES_FILE)

    if gripe_id in gripes:
        del gripes[gripe_id]
        save_gripes(gripes, GRIPES_FILE)

    return render_template("_gripes_list.html", gripes=gripes)

