from flask import Flask, request, redirect, session, send_from_directory, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- APP SETUP ----------------
app = Flask(__name__, static_folder="../static")
app.secret_key = "career_bloom_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
DB = os.path.join(BASE_DIR, "database.db")

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- AI CAREER RECOMMENDATION ENGINE ----------------
def recommend_career(profile):
    recommendations = []

    if (
        int(profile["skill_programming"]) >= 4 and
        int(profile["apt_logical"]) >= 4 and
        int(profile["skill_analytical"]) >= 4
    ):
        recommendations.append(
            ("Software Engineer",
             "Strong programming, logical thinking, and analytical skills")
        )

    if (
        int(profile["skill_creativity"]) >= 4 and
        profile["interest"] in ["Design", "Arts"]
    ):
        recommendations.append(
            ("UI/UX Designer",
             "High creativity and strong interest in design")
        )

    if (
        int(profile["skill_communication"]) >= 4 and
        int(profile["pers_leadership"]) >= 4
    ):
        recommendations.append(
            ("Management / MBA",
             "Excellent communication and leadership abilities")
        )

    if (
        int(profile["apt_numerical"]) >= 4 and
        profile["interest"] in ["Finance", "Business"]
    ):
        recommendations.append(
            ("Data Analyst",
             "Strong numerical aptitude and business interest")
        )

    if not recommendations:
        recommendations.append(
            ("Career Exploration",
             "Balanced profile – explore multiple domains before specialization")
        )

    return recommendations


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/login-page")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/forgot-password")
def forgot_page():
    return send_from_directory(FRONTEND_DIR, "forgot-password.html")

@app.route("/reset-password")
def reset_page():
    return send_from_directory(FRONTEND_DIR, "reset-password.html")

@app.route("/register-page")
def register_page():
    return send_from_directory(FRONTEND_DIR, "register.html")


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/login-page")
    return send_from_directory(FRONTEND_DIR, "home.html")


@app.route("/about")
def about():
    return send_from_directory(FRONTEND_DIR, "about.html")

@app.route("/feedback")
def feedback():
    return send_from_directory(FRONTEND_DIR, "feedback.html")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login-page")
    return send_from_directory(FRONTEND_DIR, "profile.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#----------------Feedback Email----------------
import smtplib
from email.mime.text import MIMEText

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    if "user_id" not in session:
        return redirect("/login-page")

    name = request.form["name"]
    email = request.form["email"]
    role = request.form["role"]
    experience = request.form["experience"]
    suggestions = request.form["suggestions"]

    # -------- EMAIL CONTENT --------
    subject = "New Feedback - CareerBloom"
    body = f"""
    New Feedback Received:

    Name: {name}
    Email: {email}
    Role: {role}
    Experience: {experience}

    Suggestions:
    {suggestions}
    """

    sender_email = "careerbloom2026@gmail.com"
    receiver_email = "careerbloom2026@gmail.com"
    app_password = "qezo hgxm ynic uokp"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

    return redirect("/home")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    confirm = request.form["confirm_password"]
    fav_subject = request.form["fav_subject"].lower()

    if password != confirm:
        return "Passwords do not match"

    hashed_password = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, fav_subject) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, fav_subject)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Email already exists"

    conn.close()
    return redirect("/login-page")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["user_id"]
        return redirect("/home?login=success")

    return redirect("/login-page?error=invalid")

# ---------------- FORGOT PASSWORD (NEW) ----------------
@app.route("/forgot-password", methods=["POST"])
def forgot_password_post():
    email = request.form["email"]
    subject = request.form["fav_subject"].lower().strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return redirect("/forgot-password?error=email")

    # check subject
    if user["fav_subject"].lower() != subject:
        return redirect("/forgot-password?error=subject")

    session["reset_email"] = email
    return redirect("/reset-password")

# ---------------- RESET PASSWORD (NEW) ----------------
@app.route("/reset-password", methods=["POST"])
def reset_password_post():
    if "reset_email" not in session:
        return redirect("/forgot-password")

    new_password = request.form["password"]
    hashed = generate_password_hash(new_password)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hashed, session["reset_email"])
    )
    conn.commit()
    conn.close()

    session.pop("reset_email", None)
    return redirect("/login-page?reset=success")

#-----------------CHANGE - PASSWORD-----------------
#-----------------CHANGE - PASSWORD-----------------
@app.route("/change-password", methods=["GET", "POST"])
def change_page():

    # ---------- GET ----------
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "change-password.html")

    # ---------- POST ----------
    if "user_id" not in session:
        return redirect("/login-page")

    old_password = request.form["old_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    # ❌ New password mismatch
    if new_password != confirm_password:
        return redirect("/change-password?error=nomatch")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE user_id=?",
        (session["user_id"],)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect("/change-password?error=user")

    # ❌ Wrong old password
    if not check_password_hash(user["password"], old_password):
        conn.close()
        return redirect("/change-password?error=old")

    # ✅ Update new password
    new_hashed = generate_password_hash(new_password)

    cursor.execute(
        "UPDATE users SET password=? WHERE user_id=?",
        (new_hashed, session["user_id"])
    )

    conn.commit()
    conn.close()

    # ✅ Redirect with success flag
    return redirect("/change-password?success=1")

# ---------------- SAVE / UPDATE PROFILE ----------------
@app.route("/save_profile", methods=["POST"])
def save_profile():
    if "user_id" not in session:
        return redirect("/login-page")

    data = request.form
    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id FROM profile WHERE user_id=?", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE profile SET
                age=?, gender=?, education=?,
                math_score=?, science_score=?, english_score=?, overall_score=?,
                skill_programming=?, skill_creativity=?, skill_communication=?,
                skill_problem_solving=?, skill_analytical=?,
                interest=?,
                pers_extrovert=?, pers_creative=?, pers_leadership=?, pers_risk=?,
                apt_logical=?, apt_verbal=?, apt_numerical=?
            WHERE user_id=?
        """, (
            data["age"], data["gender"], data["education"],
            data["math_score"], data["science_score"], data["english_score"], data["overall_score"],
            data["skill_programming"], data["skill_creativity"], data["skill_communication"],
            data["skill_problem_solving"], data["skill_analytical"],
            data["interest"],
            data["pers_extrovert"], data["pers_creative"],
            data["pers_leadership"], data["pers_risk"],
            data["apt_logical"], data["apt_verbal"], data["apt_numerical"],
            user_id
        ))
    else:
        cursor.execute("""
            INSERT INTO profile (
                user_id, age, gender, education,
                math_score, science_score, english_score, overall_score,
                skill_programming, skill_creativity, skill_communication,
                skill_problem_solving, skill_analytical,
                interest,
                pers_extrovert, pers_creative, pers_leadership, pers_risk,
                apt_logical, apt_verbal, apt_numerical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            data["age"], data["gender"], data["education"],
            data["math_score"], data["science_score"], data["english_score"], data["overall_score"],
            data["skill_programming"], data["skill_creativity"], data["skill_communication"],
            data["skill_problem_solving"], data["skill_analytical"],
            data["interest"],
            data["pers_extrovert"], data["pers_creative"],
            data["pers_leadership"], data["pers_risk"],
            data["apt_logical"], data["apt_verbal"], data["apt_numerical"]
        ))
    conn.commit()
    conn.close()

    return redirect("/chat")


# ---------------- GET STARTED ----------------
@app.route("/get-started")
def get_started():
    if "user_id" not in session:
        return redirect("/login-page")
    return redirect("/chat")


# ---------------- CHAT ----------------
@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login-page")
    return send_from_directory(FRONTEND_DIR, "chat.html")


@app.route("/chat-message", methods=["POST"])
def chat_message():
    if "user_id" not in session:
        return {"reply": "Please login first."}

    user_message = request.json["message"].lower().strip()
    user_id = session["user_id"]

    if "chat_stage" not in session:
        session["chat_stage"] = "start"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profile WHERE user_id=?", (user_id,))
    profile = cursor.fetchone()
    conn.close()

    if session["chat_stage"] == "start":
        if "career" in user_message:
            if not profile:
                return {"reply": "Oops! You haven’t filled your profile yet. Please complete it to get recommendations."}
            session["chat_stage"] = "confirm"
            return {"reply": "I’ve analyzed your profile. Would you like to see your career recommendations?"}
        return {"reply": "Hello! How can I help you today?"}

    if session["chat_stage"] == "confirm":
        if "yes" in user_message:
            recommendations = []

            if int(profile["skill_programming"]) >= 4 and int(profile["apt_logical"]) >= 4:
                recommendations.append("• Software Engineer – Strong programming, logical thinking, and analytical skills")

            if int(profile["skill_communication"]) >= 4 and int(profile["pers_leadership"]) >= 4:
                recommendations.append("• Management / MBA – Excellent communication and leadership abilities")

            if int(profile["skill_creativity"]) >= 4:
                recommendations.append("• UI/UX Designer – High creativity and problem-solving mindset")

            session["recommendations"] = recommendations
            session["chat_stage"] = "recommendation_shown"

            return {"reply": "Based on your profile, here are my recommendations:\n\n" + "\n".join(recommendations)}

        return {"reply": "Please say YES to continue."}

    if session["chat_stage"] == "recommendation_shown":
        session["chat_stage"] = "ask_followup"
        return {"reply": "Would you like learning paths or job roles for these careers?"}

    if session["chat_stage"] == "ask_followup":
        if "learning" in user_message:
            session["chat_stage"] = "done"
            return {"reply": "📘 Learning Paths:\n\n• Software Engineer → Python, DSA, Web Development, Git, Internships\n• Management / MBA → Business Analytics, Communication, Leadership, Case Studies\n• UI/UX Designer → Figma, UX Research, Design Thinking, Portfolio Building"}

        if "job" in user_message or "role" in user_message:
            session["chat_stage"] = "done"
            return {"reply": "💼 Job Roles:\n\n• Software Engineer → Backend Dev, Frontend Dev, Full Stack\n• Management / MBA → Business Analyst, Project Manager\n• UI/UX Designer → Product Designer, UX Researcher"}

        return {"reply": "Please type learning paths or job roles."}

    if session["chat_stage"] == "done":
        return {"reply": "If you need anything else, you can ask for another recommendation or logout anytime 😊"}


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
