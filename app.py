from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import get_connection
from config import SECRET_KEY
from chatbot import get_bot_response
app = Flask(__name__)
app.secret_key = SECRET_KEY


# Home route
@app.route('/')
def home():
    return redirect(url_for('login'))


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        enrollment = request.form['enrollment']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            'SELECT * FROM students WHERE enrollment=%s AND password=%s',
            (enrollment, password)
        )

        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student:
            session['student'] = student
            return redirect(url_for('dashboard'))
        else:
            return render_template(
                'login.html',
                error='Invalid Enrollment or Password'
            )

    return render_template('login.html')


# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'student' not in session:
        return redirect(url_for('login'))

    return render_template(
        'dashboard.html',
        student=session['student']
    )


# Attendance route
@app.route('/fees')
def fees():
    if 'student' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        'SELECT total_fee, paid_fee, pending_fee, due_date FROM fees WHERE enrollment=%s',
        (session['student']['enrollment'],)
    )

    fee_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('fees.html', fees=fee_data)


# AI Chatbot page
@app.route('/chatbot')
def chatbot():
    if 'student' not in session:
        return redirect(url_for('login'))

    return render_template('chatbot.html')


# AI Chatbot response
@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    try:
        if 'student' not in session:
            return jsonify({'response': 'Please login first.'})

        message = request.form['message']
        enrollment = session['student']['enrollment']

        print('Message:', message)
        print('Enrollment:', enrollment)

        response = get_bot_response(message, enrollment)

        print('AI Response:', response)

        return jsonify({'response': response})

    except Exception as e:
        print('ERROR:', str(e))
        return jsonify({'response': f'Error: {str(e)}'})
# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)