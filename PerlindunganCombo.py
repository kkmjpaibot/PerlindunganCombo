from flask import Flask, render_template, request, session, jsonify
import datetime
import re

from GoogleSheet import save_to_sheet, update_email_sent
from emailservice import send_summary_email

app = Flask(__name__)
app.secret_key = "not_sure_secret_key"

# -----------------------------
# Main chatbot page
# -----------------------------
@app.route('/')
def chatbot():
    return render_template('Chatbot.html')

# -----------------------------
# Submit Name
# -----------------------------
@app.route('/submit_name', methods=['POST'])
def submit_name():
    name = request.json.get('name', '').strip()
    if not name:
        return jsonify(error="Please enter your name.")

    session.clear()
    session['name'] = name

    return jsonify(
        message=f"Hello {name}! I’d love to know you a little better. When is your date of birth?"
    )

# -----------------------------
# Submit Date of Birth
# -----------------------------
@app.route('/submit_dob', methods=['POST'])
def submit_dob():
    dob = request.json.get('dob', '').strip()

    try:
        birth = datetime.datetime.strptime(dob, "%d/%m/%Y")
        today = datetime.date.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

        # Under 18 block
        if age < 18:
            return jsonify(
                blocked=True,
                message="We are sorry. This chatbot is only available for individuals aged 18 and above."
            )

        # 80 and above block
        if age >= 80:
            return jsonify(
                blocked=True,
                message="We are sorry. This chatbot is only available for individuals below 80 years old."
            )

        session['dob'] = dob
        session['age'] = age

        return jsonify(
            blocked=False,
            message=(
                f"Great, you’re {age} years old. "
                "This is a great time to plan for your protection needs.<br><br>"
                "Do you currently have insurance coverage?"
            )
        )

    except:
        return jsonify(error="Please enter date in DD/MM/YYYY format.")


# -----------------------------
# Insurance selection
# -----------------------------
@app.route('/select_insurance', methods=['POST'])
def select_insurance():
    session['insurance'] = request.json.get('insurance')
    return jsonify(message="May I know by when do you intend to be insured?")

# -----------------------------
# Timing selection
# -----------------------------
@app.route('/select_timing', methods=['POST'])
def select_timing():
    session['timing'] = request.json.get('timing')
    return jsonify(message="That’s awesome! What is your annual income range?")

# -----------------------------
# Income selection
# -----------------------------
@app.route('/select_income', methods=['POST'])
def select_income():
    session['income'] = request.json.get('income')
    return jsonify(
        message="Please enter your phone number so we can provide you with updates from time to time on suitable offers and packages."
    )

# -----------------------------
# Submit Phone
# -----------------------------
@app.route('/submit_phone', methods=['POST'])
def submit_phone():
    phone = request.json.get('phone', '').strip()
    phone_pattern = r'^(\+60|01)[0-9]{8,9}$'

    if not re.match(phone_pattern, phone):
        return jsonify(error="Invalid Malaysia phone number.")

    session['phone'] = phone

    return jsonify(
        message=(
            "<b>Let me guide you through the meaning of Perlindungan Combo.</b><br><br>"
            "Perlindungan Combo is an all-in-one protection plan that includes:<br>"
            "• Life Insurance<br>"
            "• Medical Card<br>"
            "• Critical Illness coverage"
        )
    )

# -----------------------------
# Plan preference (UPDATED)
# -----------------------------
@app.route('/select_preference', methods=['POST'])
def select_preference():
    level = int(request.json.get('level'))

    plans = {
        1: {
            "name": "Standard",
            "premium": 160,
            "life": "100,000",
            "critical": "50,000",
            "medical": "180,000"
        },
        2: {
            "name": "Basic",
            "premium": 160,
            "life": "150,000",
            "critical": "75,000",
            "medical": "180,000"
        },
        3: {
            "name": "Comprehensive",
            "premium": 300,
            "life": "200,000",
            "critical": "100,000",
            "medical": "1,000,000"
        }
    }

    plan = plans.get(level)
    session['plan'] = plan["name"]

    return jsonify({
        "plan": plan["name"],
        "premium": plan["premium"],
        "life": plan["life"],
        "critical": plan["critical"],
        "medical": plan["medical"]
    })

# -----------------------------
# Submit Email
# -----------------------------
@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.json.get('email', '').strip()
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_pattern, email):
        return jsonify(error="Invalid email format.")

    session['email'] = email
    return jsonify(message="Would you like to find out more on how you can be best protected?")

# -----------------------------
# Signup selection
# -----------------------------
@app.route('/select_signup', methods=['POST'])
def select_signup():
    session['signup'] = request.json.get('interested')

    # Save to Google Sheets
    row_index = save_to_sheet(session)

    # Send summary email
    email_sent = send_summary_email(session.get('email'), session)

    # Update email sent timestamp
    if email_sent:
        update_email_sent(row_index)

    return jsonify(
        message=(
            'Thank you for contacting us.<br>'
            'Feel free to reach out if you would like more information: '
            '<a href="https://wa.me/60168357258" target="_blank">Chat on WhatsApp</a>'
        )
    )

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
