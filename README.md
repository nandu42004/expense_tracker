# Tracker App

A simple full-stack tracker application built with **React** (frontend) and **Django REST Framework** (backend).  
The app allows managing users with basic CRUD operations.

---

## 🚀 Features
- View users
- Add new users
- Update user details
- Delete users
- Add and track expenses by category
- Monthly expense report by category

---

## 🛠️ Tech Stack
- **Frontend**: React, JavaScript, CSS  
- **Backend**: Django, Django REST Framework  
- **Database**: SQLite (default)

---

## 📂 Project Structure


cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


cd frontend
npm install
npm start
