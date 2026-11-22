# Freelancer Client & Project Management Web App

A web application built with Python, Flask, and SQLite to help freelancers organize client details, track ongoing projects, and monitor payment statuses in one place.

## Features

- **Dashboard:** View a quick summary of total clients, active projects, and payment progress.
- **Client Management:** Add, view, update, and delete client contact details and notes.
- **Project Tracking:** Link projects to specific clients and track deadlines, budgets, and completion status.
- **Database Storage:** Uses SQLite (`tracker.db`) via `database.py` to store and manage records locally.

## Project Structure

```text
├── app.py               # Main Flask application and routes
├── database.py          # SQLite database setup and queries
├── requirements.txt     # Required Python packages
├── tracker.db           # SQLite database file
├── screenshots/         # UI screenshots
├── static/              # CSS stylesheets and assets
└── templates/           # HTML templates
```

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Jinja2

## Setup & Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Saiful-Islam-Cyber/Freelancer--Client---Project-Management--Web--App.git
   cd Freelancer--Client---Project-Management--Web--App
   ```

2. **Install the required package:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in your browser:**
   Visit `http://127.0.0.1:5000`

## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Clients List
![Clients List](screenshots/clients_list.png)

### Projects List
![Projects List](screenshots/projects_list.png)

## Project Demo

Watch the full walkthrough of the Freelancer Client & Project Management Web App:
[Click here to watch the Demo Video](https://docs.google.com/videos/d/1GC9Nci01Y7Uc3GDiJMms5y0-LmMax63uy8mLR-tWDuI/play?usp=sharing)




