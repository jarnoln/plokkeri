# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plokkeri is a Django-based multi-user blogging platform. Users can create multiple blogs, write articles (in HTML or Markdown), and leave nested comments.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate secret key (required before first run)
python plokkeri/generate_passwords.py plokkeri/passwords.py

# Database migrations
./manage.py migrate
./manage.py makemigrations plok

# Run all tests
./manage.py test

# Run tests for a single app
./manage.py test plok
./manage.py test users

# Run a single test class or method
./manage.py test plok.tests.test_models.BlogModelTest
./manage.py test plok.tests.test_models.BlogModelTest.test_can_create_blog

# Start dev server
./manage.py runserver

# Deploy to production
fab deploy:host=user@hostname
```

## Architecture

### Apps

- **plok** — the main blogging app: models, views, templates, URL config, and tests
- **users** — user profile management (CRUD views around Django's built-in `User` model; auth itself is handled by django-allauth)

### Models (`plok/models.py`)

Three core models, each with `created_by`/`edited_by` FK fields and a `can_edit(user)` method:

- **Blog** — owned by a user; uniquely named; contains articles
- **Article** — belongs to a Blog; supports `format` field (`html` or `md`); markdown is rendered in the view, not stored
- **Comment** — belongs to an Article; optional `reply_to` FK pointing at another Comment (nesting)

### Views

The `plok` app splits views across multiple files rather than a single `views.py`:
- `views.py` — homepage (article list)
- `blog.py` — Blog CRUD (ListView, DetailView, CreateView, UpdateView, DeleteView)
- `article.py` — Article CRUD; applies `markdown.markdown()` for `md`-format articles before passing to templates
- `comment.py` — Comment CRUD
- `about.py` — static about page with markdown rendering

### URL routing

```
/              → plok article index (homepage)
/plok/         → plok app URLs (blog, article, comment endpoints)
/user/         → users app URLs (profile, edit, delete)
/accounts/     → django-allauth (login, signup, OAuth: GitHub, Google, Twitter, Amazon)
/admin/        → Django admin
/i18n/         → language switching
```

### Permission model

All content is owner-only editable. `can_edit(user)` returns `True` if `user == obj.created_by` or `user.is_staff`. Views enforce `LoginRequiredMixin` and check `can_edit` before allowing mutations.

### Testing patterns

Tests live in `plok/tests/` (split by domain: `test_models.py`, `test_views.py`, `test_article.py`, `test_comment.py`) and `users/tests/`. The shared base class `ExtTestCase` in each test module handles user creation and login setup — extend it instead of `TestCase` when tests need an authenticated user.

### Settings & secrets

`plokkeri/settings.py` imports `SECRET_KEY` and database credentials from `plokkeri/passwords.py`, which is git-ignored and generated locally by `generate_passwords.py`. This file must exist before `runserver` or tests will fail.

### Deployment

- **Ansible** (`ansible/provision-deb.yaml`) provisions a Debian server (nginx, gunicorn systemd service)
- **Fabric** (`fabfile.py`) deploys: pulls source, installs deps, runs migrations, collects static files, restarts gunicorn
