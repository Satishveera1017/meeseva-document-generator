# Meeseva – Aadhaar & PAN Document Generation System

Meeseva is a Django-based web application designed to generate Aadhaar and PAN
documents from user-provided details. The application provides document
generation, masked and unmasked downloads, and email-based document delivery.

## Features

- Generate Aadhaar number
- Generate PAN number
- User details form
- Download Aadhaar document
- Download masked Aadhaar
- Download unmasked Aadhaar
- Download PAN document
- Send generated documents through email
- Gmail SMTP email integration
- Loading animation during PAN document generation
- Responsive web interface

## Tech Stack

### Backend
- Python
- Django

### Frontend
- HTML5
- CSS3
- JavaScript

### Database
- SQLite

### Email
- Gmail SMTP
- Django Email Backend

### Development Tools
- Visual Studio Code
- Git
- GitHub

## Project Structure

```text
meeseva/
│
├── meeseva/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── home/
│   ├── views.py
│   ├── models.py
│   └── ...
│
├── templates/
├── media/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md