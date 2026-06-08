import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, g, flash, abort

app = Flask(__name__)


DATABASE = os.path.join(os.path.dirname(__file__), "blog.db")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                excerpt TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (post_id, tag_id)
            );
        """)
        db.commit()

        # Seed with sample posts if empty
        count = db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        if count == 0:
            sample_posts = [
                (
                    "Hello, World!",
                    "hello-world",
                    "Welcome to my personal blog. This is a space where I share my thoughts, experiences, and ideas on topics I find fascinating.\n\nI built this blog from scratch using Python and SQLite — no heavy frameworks, just simple, clean code. I wanted something minimal that I actually own and understand completely.\n\nExpect posts about technology, philosophy, and the occasional creative writing piece. Stay curious.",
                    "Welcome to my corner of the internet.",
                    "2026-05-01 09:00:00",
                    "2026-05-01 09:00:00",
                ),
                (
                    "Why I Write",
                    "why-i-write",
                    "Writing is thinking made visible. When I type out an idea, I'm forced to confront whether I actually understand it — or whether I've been fooling myself with vague intuitions.\n\nThere's a well-known concept called the Feynman Technique: if you can't explain something simply, you don't understand it yet. Writing is my Feynman Technique. It's humbling and clarifying in equal measure.\n\nI write to think, to remember, and occasionally to connect with someone somewhere who might find something useful in these words.",
                    "Writing is thinking made visible.",
                    "2026-05-15 14:30:00",
                    "2026-05-15 14:30:00",
                ),
                (
                    "Notes on Simplicity",
                    "notes-on-simplicity",
                    "The best tools get out of your way. A good knife, a plain text editor, a quiet room — these things don't demand attention. They just work.\n\nI've been thinking about this in software. We keep adding abstractions on top of abstractions until no one person can hold the whole system in their head. Complexity compounds silently.\n\nSimplicity is not about doing less. It's about doing exactly what's needed — no more, no less. That takes discipline, which is why it's rare.",
                    "The best tools get out of your way.",
                    "2026-06-01 11:00:00",
                    "2026-06-01 11:00:00",
                ),
            ]
            for post in sample_posts:
                db.execute(
                    "INSERT INTO posts (title, slug, content, excerpt, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                    post,
                )
            db.commit()


def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


def format_date(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%B %d, %Y")
    except Exception:
        return dt_str


app.jinja_env.filters["format_date"] = format_date


# ── Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT * FROM posts ORDER BY created_at DESC"
    ).fetchall()
    return render_template("index.html", posts=posts)


@app.route("/post/<slug>")
def post(slug):
    db = get_db()
    p = db.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
    if p is None:
        abort(404)
    return render_template("post.html", post=p)


@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Title and content are required.", "error")
            return render_template("edit.html", post=None, form=request.form)

        slug = slugify(title)
        excerpt = content[:120].rstrip() + ("…" if len(content) > 120 else "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()

        # Ensure unique slug
        base_slug, n = slug, 1
        while db.execute("SELECT id FROM posts WHERE slug = ?", (slug,)).fetchone():
            slug = f"{base_slug}-{n}"
            n += 1

        db.execute(
            "INSERT INTO posts (title, slug, content, excerpt, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (title, slug, content, excerpt, now, now),
        )
        db.commit()
        flash("Post published!", "success")
        return redirect(url_for("post", slug=slug))

    return render_template("edit.html", post=None, form={})


@app.route("/edit/<slug>", methods=["GET", "POST"])
def edit_post(slug):
    db = get_db()
    p = db.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
    if p is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Title and content are required.", "error")
            return render_template("edit.html", post=p, form=request.form)

        excerpt = content[:120].rstrip() + ("…" if len(content) > 120 else "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE posts SET title=?, content=?, excerpt=?, updated_at=? WHERE slug=?",
            (title, content, excerpt, now, slug),
        )
        db.commit()
        flash("Post updated!", "success")
        return redirect(url_for("post", slug=slug))

    return render_template("edit.html", post=p, form=dict(p))


@app.route("/delete/<slug>", methods=["POST"])
def delete_post(slug):
    db = get_db()
    db.execute("DELETE FROM posts WHERE slug = ?", (slug,))
    db.commit()
    flash("Post deleted.", "success")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
