from google import genai
from dotenv import load_dotenv
import os
from database import get_connection

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def get_bot_response(message, enrollment):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        'SELECT subject, percentage FROM attendance WHERE enrollment=%s',
        (enrollment,)
    )
    attendance = cursor.fetchall()

    cursor.execute(
        'SELECT total_fee, paid_fee, pending_fee, due_date FROM fees WHERE enrollment=%s',
        (enrollment,)
    )
    fees = cursor.fetchone()

    cursor.execute(
        'SELECT subject, exam_date, exam_time FROM exams ORDER BY exam_date LIMIT 5'
    )
    exams = cursor.fetchall()

    cursor.close()
    conn.close()

    prompt = f'''
You are the official GNIOT AI Student Support Assistant.

Student attendance:
{attendance}

Fee details:
{fees}

Upcoming exams:
{exams}

Student question:
{message}

Answer naturally and accurately using the database information above.
'''

    response = client.models.generate_content(
        model='models/gemini-3.5-flash',
        contents=prompt
    )

    return response.text