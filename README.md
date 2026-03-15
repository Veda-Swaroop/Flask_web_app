# BookStore — Full-Stack Flask Web Application

A full-stack online bookstore built with **Python/Flask** while learning backend web development — covering user authentication, shopping cart and order flow, ORM modeling, and cloud deployment on AWS EC2. The catalog contains 12,000 books with cover art sourced from the Open Library API.

**Live Demo:** [devport.co.in](https://devport.co.in)

---

## Features

- **User Authentication** — Register, login from the landing page, and logout with Flask-Login and secure session management
- **Password Reset** — Users can reset their password by verifying their account details in-app
- **Shopping Cart** — Add, update, and remove books from a persistent cart tied to each user
- **Order Management** — Place orders, view order confirmation, and browse order history
- **Book Catalog** — Browse 12,000 books with cover images sourced from the Open Library Covers API
- **Search & Filter** — Find books by title, author, or genre
- **Admin Panel** — View and manage registered users; admin can delete user accounts
- **Responsive UI** — Mobile-friendly layout built with Bootstrap 5
- **Cloud Deployed** — Hosted on AWS EC2 with a custom domain and HTTPS

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask |
| **Database** | PostgreSQL + SQLAlchemy ORM (2.0 style) |
| **Auth** | Flask-Login |
| **Forms** | Flask-WTF |
| **Templating** | Jinja2 |
| **Frontend** | Bootstrap 5, JavaScript |
| **Deployment** | AWS EC2 (Ubuntu), Gunicorn / Nginx |
| **Book Covers** | Open Library Covers API |

---

## Database Models

```
User ──< Order ──< OrderItem >── Book
User ──< Cart  ──< CartItem  >── Book
```

- **User** — Stores account credentials and profile info
- **Book** — Catalog of books with metadata and cover image references
- **Cart** — One active cart per user
- **CartItem** — Line items linking books to a cart with quantity
- **Order** — A confirmed purchase placed by a user
- **OrderItem** — Line items capturing book, quantity at time of order

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.10+
- PostgreSQL

### Installation

```bash
# Clone the repository
git clone https://github.com/Veda-Swaroop/Flask_web_app.git
cd Flask_web_app

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a PostgreSQL database
createdb bookstore_db

# Configure environment variables
cp .env.example .env
# Edit .env and fill in DATABASE_URL and SECRET_KEY

# Set up the database tables
flask db upgrade

# Run the development server
python run.py
```

Visit `http://localhost:5000` in your browser.

---

## Project Structure

```
FLASK_WEB_APP/
├── app/
│   ├── admin/                       # Admin blueprint
│   │   ├── __init__.py
│   │   └── routes.py                # View users, delete user accounts
│   ├── auth/                        # Auth blueprint
│   │   ├── __init__.py
│   │   └── routes.py                # Login, register, password reset
│   ├── main/                        # Main blueprint
│   │   ├── __init__.py
│   │   └── routes.py                # Catalog, book detail, cart, orders
│   ├── static/
│   │   ├── covers/                  # Book cover images — not included in repo (see note below)
│   │   ├── images/                  # App images for carousel
│   │   └── favicon.ico
│   ├── templates/
│   │   ├── layout.html              # Base template
│   │   ├── index.html               # Landing page with login form
│   │   ├── home.html                # Main catalog / browse page (post-login)
│   │   ├── book_detail.html         # Individual book page
│   │   ├── cart.html                # Shopping cart
│   │   ├── order.html               # Order summary
│   │   ├── order_confirmation.html  # Post-purchase confirmation
│   │   ├── my_orders.html           # User order history
│   │   ├── register.html            # Registration form
│   │   ├── verify.html              # Identity verification step for password reset
│   │   ├── reset.html               # Password reset page
│   │   ├── logout.html              # Logout confirmation
│   │   └── admin.html               # Admin panel — user list and delete
│   ├── __init__.py                  # App factory
│   ├── extensions.py                # Flask extensions (db, login_manager, migrate)
│   ├── forms.py                     # Flask-WTF form definitions
│   └── models.py                    # SQLAlchemy ORM models
├── migrations/                      # Flask-Migrate migration files
├── .env                             # Environment variables (not committed)
├── .gitignore
├── LICENSE
├── run.py                           # Development entry point
└── wsgi.py                          # Production WSGI entry point (Gunicorn)
```

---

## Deployment

The app is deployed on **AWS EC2** (Ubuntu) using:

- **Gunicorn** as the WSGI server (via `wsgi.py`)
- **Nginx** as the reverse proxy
- **PostgreSQL** running on the EC2 instance
- A custom domain with HTTPS via Let's Encrypt / Certbot

---

## Notable Engineering Details

- Organized routes using **Flask Blueprints** (`admin`, `auth`, `main`) for clean separation of concerns and maintainability
- Managed Flask extensions in a dedicated `extensions.py` to avoid circular imports — a common pitfall in larger Flask apps
- Used **SQLAlchemy 2.0** `Mapped`/`mapped_column` syntax for type-safe, modern ORM models
- Built a **password reset flow** in the auth blueprint — users verify their identity against the database and reset their password in-app
- The **cart → order flow** snapshots price at time of purchase in `OrderItem`, protecting order history against future price changes
- Book cover images (~8,000–9,000 images) were downloaded from the **Open Library Covers API** and served from `static/covers/` — this folder is excluded from the repo due to GitHub storage limits (see note below)
- Implemented **toast notifications** via JavaScript for cart actions without full page reloads
- Used the **Post/Redirect/Get** pattern on order confirmation to prevent duplicate order submissions on page refresh

---

## Book Covers Note

The `app/static/covers/` folder is **not included in this repository**. It contains ~8,000–9,000 cover images for the 12,000-book catalog, which exceeds GitHub's recommended repository size limits.

The covers were downloaded from the [Open Library Covers API](https://openlibrary.org/dev/docs/api#anchor_images). To run the app locally with cover images:

1. Create the folder: `app/static/covers/`
2. For each book in your database, fetch its cover from Open Library using its ISBN:
   ```
   https://covers.openlibrary.org/b/isbn/{ISBN}-L.jpg
   ```
3. Save each image as `{bookID}.jpg` inside the `covers/` folder

Books without a cover image will fall back to a placeholder automatically.

---

## Screenshots

**Login / Landing**
<p align="center">
    <img src="screenshots/login.png" alt="login" width="600">
</p>

**Home / Catalog**
<p align="center">
    <img src="screenshots/home.png" alt="home" width="600">
</p>

**Book Detail**
<p align="center">
    <img src="screenshots/book_details.png" alt="book_details" width="600">
</p>

**Shopping Cart**
<p align="center">
    <img src="screenshots/cart.png" alt="shopping_cart" width="600">
</p>

**Order Confirmation**
<p align="center">
    <img src="screenshots/order.png" alt="order_confirmation" width="600">
</p>

**Order History**
<p align="center">
    <img src="screenshots/order_history.png" alt="order_history" width="600">
</p>

---

## License

This project is open source and available under the [MIT License](LICENSE).