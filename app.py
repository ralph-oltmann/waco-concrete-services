from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("waco.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            job_name TEXT,
            address TEXT,
            status TEXT,
            priority INTEGER,
            next_action TEXT,
            waiting_reason TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def dashboard():
    conn = sqlite3.connect("waco.db")
    c = conn.cursor()
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()
    conn.close()

    ready = sorted([j for j in jobs if j[4] == "READY"], key=lambda x: x[5], reverse=True)
    active = [j for j in jobs if j[4] == "ACTIVE"]
    waiting = [j for j in jobs if j[4] == "WAITING"]

    return render_template("dashboard.html", ready=ready, active=active, waiting=waiting)

@app.route("/add", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        conn = sqlite3.connect("waco.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO jobs (customer, job_name, address, status, priority, next_action, waiting_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["customer"],
            request.form["job_name"],
            request.form["address"],
            "READY",
            request.form["priority"],
            request.form["next_action"],
            ""
        ))

        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("add_job.html")

@app.route("/update/<int:job_id>/<status>")
def update_status(job_id, status):
    conn = sqlite3.connect("waco.db")
    c = conn.cursor()
    c.execute("UPDATE jobs SET status=? WHERE id=?", (status, job_id))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/wait/<int:job_id>", methods=["POST"])
def set_waiting(job_id):
    reason = request.form["reason"]

    conn = sqlite3.connect("waco.db")
    c = conn.cursor()
    c.execute("""
        UPDATE jobs
        SET status='WAITING', waiting_reason=?
        WHERE id=?
    """, (reason, job_id))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
