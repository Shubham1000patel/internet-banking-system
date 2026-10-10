INTERNET BANKING SYSTEM
=======================

Overview
--------
This project is an educational internet banking application. It includes a
FastAPI backend, a MySQL database connection, and a browser-based frontend.
Features include customer registration and login, accounts, balances,
deposits, withdrawals, transfers, beneficiaries, bill payments, transaction
history, and administrator operations.

Requirements
------------
- Python 3.10 or newer
- MySQL Server
- pip

Setup
-----
1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

   Windows PowerShell:
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1

   Windows Command Prompt:
     py -m venv .venv
     .\.venv\Scripts\activate.bat

3. Install the Python packages used by the application:

     python -m pip install fastapi uvicorn mysql-connector-python python-dotenv PyJWT bcrypt email-validator pytest

4. Create a MySQL database named internet_banking, or set DB_NAME to the
   database name you use. Create the tables required by the application
   repositories before starting the app.

5. Create a local .env file in the project folder with your own values:

     DB_HOST=localhost
     DB_USER=root
     DB_PASSWORD=your_mysql_password
     DB_NAME=internet_banking
     JWT_SECRET_KEY=replace_with_a_long_random_secret
     JWT_ALGORITHM=HS256
     JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

   Do not upload .env or real passwords/secrets to GitHub. The application
   requires JWT_SECRET_KEY to be set.

Run the backend
---------------
From the project folder, with the virtual environment activated, run:

     uvicorn main:app --reload

The API will be available at:
  http://127.0.0.1:8000

Interactive API documentation:
  http://127.0.0.1:8000/docs

Health check:
  http://127.0.0.1:8000/health

Run the frontend
----------------
The frontend files are in the frontend folder. Its API client currently uses
http://127.0.0.1:8000 as the backend address, so start the backend first.

In a second terminal, from the project folder, start a local static file
server:

     python -m http.server 5500 --directory frontend

Then open:
  http://127.0.0.1:5500/

Tests
-----
With the project dependencies installed, run:

     python -m pytest

Project layout
--------------
- main.py          FastAPI application and API endpoints
- services/        Application and business logic
- repositories/    Database access
- schemas/         Request and response models
- frontend/        HTML, CSS, and JavaScript interface
- tests/           Automated tests

Notes
-----
- Database table definitions or migration scripts are not included in this
  project directory; provision the tables expected by the repositories.
- Keep credentials and JWT secrets private. Use placeholder values only in
  any example configuration shared publicly.

