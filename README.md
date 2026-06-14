# 🎬 CineVault – Movie Management System

A complete desktop movie management system built with Python, CustomTkinter, and MongoDB.

---

## ✨ Features

### Authentication
- Registration with full validation (email, username uniqueness, password strength)
- Login with password hashing (bcrypt)
- Remember Me option
- Forgot Password / reset
- Role-based redirect (Admin / User)

### Admin Dashboard
- **Stats Overview** – Total movies, users, genres, reviews, avg rating
- **Movie CRUD** – Add, view, edit, delete movies with search/filter/sort
- **User Management** – View, edit, block, activate, delete users
- **Genre CRUD** – Create and manage genres
- **Review Management** – View and delete reviews with filtering
- **Reports** – Export to PDF, Excel, CSV

### User Dashboard
- **Home** – Personalized greeting with stats cards and recently added movies
- **Browse Movies** – Search, filter by genre, sort; card grid with detail popup
- **Movie Details** – Full info, trailer link, add to favorites, write review
- **My Favorites** – Saved movies with remove option
- **My Reviews** – View, edit, delete your own reviews
- **Profile** – Update name/email, change password

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.9+
- MongoDB running on `localhost:27017`
- VS Code (recommended)

### 1. Install dependencies
```bash
cd MovieManagementSystem
pip install -r requirements.txt
```

### 2. Seed sample data (optional but recommended)
```bash
python seed_data.py
```
This creates:
- 8 movies across various genres
- Admin account: `admin / admin123`
- User accounts: `alice / alice123`, `bob / bob123`

### 3. Run the application
```bash
python main.py
```

---

## 📁 Project Structure
```
MovieManagementSystem/
├── main.py                    # Entry point + splash screen
├── theme.py                   # Shared design tokens & helper widgets
├── base_dashboard.py          # Sidebar scaffold (shared by Admin & User)
├── seed_data.py               # Sample data loader
├── requirements.txt
│
├── config/
│   └── database.py            # MongoDB connection & collections
│
├── authentication/
│   ├── login.py               # Login form
│   ├── register.py            # Registration form
│   └── forgot_password.py     # Password reset
│
├── admin/
│   ├── dashboard.py           # Admin dashboard + stats
│   ├── movies.py              # Movie CRUD + reusable table
│   ├── users.py               # User management
│   ├── genres.py              # Genre CRUD
│   ├── reviews.py             # Review management
│   └── reports.py             # PDF/Excel/CSV export
│
├── user/
│   ├── dashboard.py           # User dashboard + home
│   ├── browse_movies.py       # Movie browser + detail + review dialog
│   ├── favorites.py           # Favorites list
│   ├── reviews.py             # User's own reviews
│   └── profile.py            # Profile + password change
│
├── assets/                    # Images & icons
└── reports/                   # Generated report files
```

---

## 🛠 MongoDB Collections

| Collection  | Description              |
|-------------|--------------------------|
| `users`     | User accounts            |
| `movies`    | Movie catalog            |
| `genres`    | Genre definitions        |
| `reviews`   | User reviews             |
| `favorites` | User favorite movies     |
| `reports`   | (Reserved for logs)      |

---

## 🎨 Design

- **Theme**: Dark cinema aesthetic with amber accent (#E8A020)
- **Framework**: CustomTkinter for modern rounded widgets
- **Typography**: Georgia (display) + Trebuchet MS (body)
- **Layout**: Sidebar navigation + scrollable content area

---

## 📦 Dependencies

| Package        | Purpose                    |
|----------------|----------------------------|
| customtkinter  | Modern Tkinter UI framework |
| pillow         | Image handling             |
| pymongo        | MongoDB driver             |
| bcrypt         | Password hashing           |
| pandas         | Data processing            |
| reportlab      | PDF generation             |
| openpyxl       | Excel export               |
| tkcalendar     | Date picker                |
