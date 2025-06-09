<p align="center">
  <img src="library_manager/frontend/public/images/library_seal.jpg" alt="LibManager Logo" width="200"/>
</p>

<h1 align="center">LibManager: A Full-Stack Library Management System</h1>

<p align="center">
  A comprehensive web application developed for the <strong>INF-2900 Software Engineering</strong> course at <strong>UiT The Arctic University of Norway</strong>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.0-green?style=for-the-badge&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/React-18.2-blue?style=for-the-badge&logo=react" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5.2-blue?style=for-the-badge&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql" alt="MySQL">
</p>

## 🌟 About The Project

LibManager is a full-stack web application designed to modernize library operations. It provides an intuitive platform for both librarians and patrons to manage, browse, and borrow books. This project was our capstone for the **INF-2900 Software Engineering** course, where we applied agile methodologies, full-stack development principles, and collaborative software engineering practices to build a real-world application from the ground up.

Our goal was to create a system that is not only functional and secure but also user-friendly and maintainable, demonstrating our readiness for professional software development roles.

## ✨ Key Features

- **Role-Based Access Control:** Separate views and permissions for regular Users, Librarians, and Administrators.
- **Full-Stack Authentication:** Secure user registration, login, and session management with CSRF protection.
- **Dynamic Book Catalog:** Browse, search, and filter books. Features an interactive carousel view and flip-card details.
- **CRUD Operations for Books:** Librarians and Admins can easily add, update, and delete books from the catalog.
- **Borrowing & Returning System:** Users can borrow up to three books and view their borrowing history on their profile.
- **User Profile Management:** Users can update their profile information and choose a custom avatar.
- **Admin Dashboard:** Administrators can manage all users, including promoting users to librarian status.

## 💻 Technology Stack

Our project is built with a modern, robust technology stack:

- **Backend:**
  - **Python** with **Django** & **Django REST Framework**
  - **WhiteNoise** for serving static files
- **Frontend:**
  - **React** with **TypeScript**
  - **Vite** for the build tool
  - **Framer Motion** & **React Slick** for animations and carousels
- **Database:**
  - **MySQL**
- **Testing & DevOps:**
  - **Backend:** `unittest` (via Django's test runner), `coverage.py`
  - **Frontend:** **Vitest** (Component), **Cypress** (End-to-End)
  - **Version Control:** **Git** & **GitHub**
  - **Project Management:** **Jira**
  - **Automation:** Bash & Batch scripts for streamlined setup and testing.

## 🏛️ Architecture

LibManager is designed using a **Client-Server architecture**.

- The **Frontend (Client)** is a single-page application built with **React**, featuring a component-based structure for a modular and maintainable UI.
- The **Backend (Server)** is a monolithic application built with **Django**, following the **Model-View-Template (MVT)** pattern. It exposes a **RESTful API** using Django REST Framework to handle all business logic and data manipulation.
- The client and server communicate via stateless HTTP requests, ensuring a clear separation of concerns.

## 👥 Our Team

This project was a collaborative effort by the following agile software engineers:

- Alvaro
- Carlos
- Julius
- Matt

## 🚀 Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

- [Node.js](https://nodejs.org/en/) & [npm](https://www.npmjs.com/)
- [Python](https://www.python.org/) (v3.9+)
- [MySQL Server](https://dev.mysql.com/downloads/installer/)

### Installation & Setup

We have created automation scripts to simplify the entire setup and launch process!

**1. Clone the repository:**
```bash
git clone <repository-url>
cd INF_2900_TEAM5
```

**2. Set up the Database:**
You need a local MySQL server running.
- Create a database named `library_test`.
- The application is configured to use the user `root` with the password `SoftwareUser` on `localhost:3306`. You can adjust this in `library_manager/settings.py`.

> 🗄️ For detailed instructions on setting up MySQL, especially for WSL users, please see our **[MySQL Setup Guide](README_MYSQL.md)**.

**3. Run the Automated Launch Scripts:**
These scripts create a Python virtual environment, install all backend and frontend dependencies, run database migrations, and start the servers.

**On Windows:**
In your first terminal, start the backend:
```bat
# This script handles venv, installs dependencies, runs migrations, and starts the Django server.
Windows_start_backend.bat
```
Then, in a **new terminal**, start the frontend:
```bat
# This script navigates to the frontend folder, installs npm packages, and starts the React dev server.
Windows_start_frontend.bat
```

**On Linux/macOS:**
First, make the scripts executable:
```bash
chmod +x Linux_start_backend.sh Linux_start_frontend.sh
```
In your first terminal, start the backend:
```bash
./Linux_start_backend.sh
```
Then, in a **new terminal**, start the frontend:
```bash
./Linux_start_frontend.sh
```

**4. Access the Application:**
Once both servers are running, open your browser and navigate to the frontend development server's URL:
- **[http://localhost:5173/](http://localhost:5173/)**

The React frontend will automatically connect to the Django backend API running on `http://localhost:8000`.

## 🧪 Running Tests

We have implemented a comprehensive testing strategy covering the entire application, including unit, functional, security, and end-to-end tests. We also created automated test runner scripts.

**To run all tests automatically:**
- **On Windows:** `Windows_run_tests.bat`
- **On Linux/macOS:** `./Linux_run_tests.sh` (make sure to `chmod +x` it first)

> 🔬 For detailed instructions on running specific test suites (backend, frontend, E2E) and generating coverage reports, please see our **[Testing Guide](README_TEST.md)**.

## 📜 Project Documentation

As part of our software engineering course, we maintained extensive documentation covering our process and design decisions. This includes our user stories, architectural diagrams, sprint planning (using Jira), and reflections on the agile process. This demonstrates our commitment to not just writing code, but also to planning, documenting, and reflecting on our work like a professional engineering team.
**[Group Report](docs/Software%20Engineering%20Group%20Report.pdf)**
```