# A Personal Blog

A clean personal blog built with Python (Flask), SQLite, and hand-crafted HTML/CSS.

## Features
- Write, edit, and delete posts
- Auto-generated URL slugs from titles
- Excerpt auto-generated from content
- Drop-cap first letter on post pages
- Editorial magazine aesthetic
- Fully responsive

## Setup

```bash
# 1. Install dependency
pip install flask

# 2. Run the app (database is created automatically)
python app.py
```

Then open **http://localhost:5000** in your browser.

## Project Structure

```
blog/
├── app.py              # Flask app & routes
├── blog.db             # SQLite database (auto-created)
├── templates/
│   ├── base.html       # Shared layout
│   ├── index.html      # Post list
│   ├── post.html       # Single post
│   ├── edit.html       # New / edit post form
│   └── 404.html        # Error page
└── static/
    └── css/
        └── style.css   # All styles
```

## Usage

| Action      | URL                   |
|-------------|-----------------------|
| Home        | `/`                   |
| Read post   | `/post/<slug>`        |
| New post    | `/new`                |
| Edit post   | `/edit/<slug>`        |
| Delete post | `POST /delete/<slug>` |
