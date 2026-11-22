import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from database import get_db_connection, init_db, get_dashboard_stats

app = Flask(__name__)
app.secret_key = "saiful_freelance_tracker_2026"

# Initialize tables on startup
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    
    # Handle adding a new project
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        client_id = request.form.get("client_id")
        budget = request.form.get("budget", "").strip()
        deadline = request.form.get("deadline", "").strip()
        status = request.form.get("status", "Pending")
        is_paid = 1 if request.form.get("is_paid") == "on" else 0

        # Input validation
        if not title or not client_id or not budget or not deadline:
            flash("All project fields are required.", "error")
        else:
            try:
                budget_val = float(budget)
                if budget_val < 0:
                    raise ValueError
                conn.execute(
                    "INSERT INTO projects (client_id, title, budget, deadline, status, is_paid) VALUES (?, ?, ?, ?, ?, ?)",
                    (client_id, title, budget_val, deadline, status, is_paid)
                )
                conn.commit()
                flash("Project added successfully!", "success")
                return redirect(url_for("index"))
            except ValueError:
                flash("Budget must be a valid positive number.", "error")

    # Search and filter logic
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "")

    query = """
        SELECT projects.*, clients.name AS client_name 
        FROM projects 
        JOIN clients ON projects.client_id = clients.id
        WHERE 1=1
    """
    params = []

    if search_query:
        query += " AND (projects.title LIKE ? OR clients.name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if status_filter:
        query += " AND projects.status = ?"
        params.append(status_filter)

    query += " ORDER BY projects.deadline ASC"
    
    projects = conn.execute(query, params).fetchall()
    clients = conn.execute("SELECT * FROM clients ORDER BY name ASC").fetchall()
    conn.close()

    stats = get_dashboard_stats()
    return render_template(
        "index.html",
        projects=projects,
        clients=clients,
        stats=stats,
        search_query=search_query,
        status_filter=status_filter
    )

@app.route("/project/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    
    if not project:
        conn.close()
        flash("Project not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        client_id = request.form.get("client_id")
        budget = request.form.get("budget", "").strip()
        deadline = request.form.get("deadline", "").strip()
        status = request.form.get("status")
        is_paid = 1 if request.form.get("is_paid") == "on" else 0

        if not title or not client_id or not budget or not deadline:
            flash("Please fill out all required fields.", "error")
        else:
            try:
                budget_val = float(budget)
                if budget_val < 0:
                    raise ValueError
                conn.execute("""
                    UPDATE projects 
                    SET client_id = ?, title = ?, budget = ?, deadline = ?, status = ?, is_paid = ?
                    WHERE id = ?
                """, (client_id, title, budget_val, deadline, status, is_paid, project_id))
                conn.commit()
                conn.close()
                flash("Project updated!", "success")
                return redirect(url_for("index"))
            except ValueError:
                flash("Budget must be a valid positive number.", "error")

    clients = conn.execute("SELECT * FROM clients ORDER BY name ASC").fetchall()
    conn.close()
    return render_template("edit_project.html", project=project, clients=clients)

@app.route("/project/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    flash("Project deleted.", "success")
    return redirect(url_for("index"))

# --- CLIENT MANAGEMENT ROUTES ---

@app.route("/clients", methods=["GET", "POST"])
def clients():
    conn = get_db_connection()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()

        if not name or not email or "@" not in email:
            flash("Please enter a valid client name and email address.", "error")
        else:
            conn.execute(
                "INSERT INTO clients (name, email, company) VALUES (?, ?, ?)",
                (name, email, company)
            )
            conn.commit()
            flash("Client added!", "success")
            return redirect(url_for("clients"))

    all_clients = conn.execute("SELECT * FROM clients ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("clients.html", clients=all_clients)

@app.route("/client/edit/<int:client_id>", methods=["GET", "POST"])
def edit_client(client_id):
    conn = get_db_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    
    if not client:
        conn.close()
        flash("Client not found.", "error")
        return redirect(url_for("clients"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()

        if not name or not email or "@" not in email:
            flash("Valid name and email are required.", "error")
        else:
            conn.execute(
                "UPDATE clients SET name = ?, email = ?, company = ? WHERE id = ?",
                (name, email, company, client_id)
            )
            conn.commit()
            conn.close()
            flash("Client details updated!", "success")
            return redirect(url_for("clients"))

    conn.close()
    return render_template("edit_client.html", client=client)

@app.route("/client/delete/<int:client_id>", methods=["POST"])
def delete_client(client_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    flash("Client and their associated projects deleted.", "success")
    return redirect(url_for("clients"))

# --- CSV REPORT EXPORT ---

@app.route("/export/csv")
def export_csv():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT projects.id, projects.title, clients.name, projects.budget, projects.deadline, projects.status, projects.is_paid
        FROM projects
        JOIN clients ON projects.client_id = clients.id
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Project ID", "Title", "Client", "Budget ($)", "Deadline", "Status", "Payment Status"])

    for r in rows:
        paid_text = "Paid" if r["is_paid"] == 1 else "Unpaid"
        writer.writerow([r["id"], r["title"], r["name"], r["budget"], r["deadline"], r["status"], paid_text])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=projects_report.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)

