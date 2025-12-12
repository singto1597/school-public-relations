import os
import psycopg2
import requests
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from datetime import date

SCHEDULE_TEMPLATES = {
    "normal_50": [
        {
            "period": "เข้าแถว",
            "start": "07:45",
            "end": "08:30"
        },
        {
            "period": "คาบ 1",
            "start": "08:30",
            "end": "09:20"
        },
        {
            "period": "คาบ 2",
            "start": "09:20",
            "end": "10:10"
        },
        {
            "period": "พัก 20",
            "start": "10:10",
            "end": "10:30"
        },
        {
            "period": "คาบ 3",
            "start": "10:30",
            "end": "11:20"
        },
        {
            "period": "คาบ 4",
            "start": "11:20",
            "end": "12:10"
        },
        {
            "period": "คาบ 5",
            "start": "12:10",
            "end": "13:00"
        },
        {
            "period": "คาบ 6",
            "start": "13:00",
            "end": "13:50"
        },
        {
            "period": "คาบ 7",
            "start": "13:50",
            "end": "14:40"
        },
        {
            "period": "คาบ 8",
            "start": "14:40",
            "end": "15:30"
        },
        {
            "period": "คาบ 9",
            "start": "15:30",
            "end": "16:20"
        }
    ],
    "short_40": [
        {
            "period": "เข้าแถว",
            "start": "07:45",
            "end": "08:30"
        },
        {
            "period": "คาบ 1",
            "start": "08:30",
            "end": "09:10"
        },
        {
            "period": "คาบ 2",
            "start": "09:10",
            "end": "09:50"
        },
        {
            "period": "พัก 20",
            "start": "09:50",
            "end": "10:10"
        },
        {
            "period": "คาบ 3",
            "start": "10:10",
            "end": "10:50"
        },
        {
            "period": "คาบ 4",
            "start": "10:50",
            "end": "11:30"
        },
        {
            "period": "คาบ 5",
            "start": "11:30",
            "end": "12:10"
        },
        {
            "period": "คาบ 6",
            "start": "12:10",
            "end": "12:50"
        },
        {
            "period": "คาบ 7",
            "start": "12:50",
            "end": "13:30"
        },
        {
            "period": "คาบ 8",
            "start": "13:50",
            "end": "14:10"
        },
        {
            "period": "คาบ 9",
            "start": "14:10",
            "end": "14:50"
        }
    ],
    "even_50": [
        {
            "period": "เข้าแถว",
            "start": "07:45",
            "end": "09:00"
        },
        {
            "period": "คาบ 1",
            "start": "09:00",
            "end": "09:40"
        },
        {
            "period": "คาบ 2",
            "start": "09:40",
            "end": "10:20"
        },
        {
            "period": "พัก 20",
            "start": "10:20",
            "end": "10:40"
        },
        {
            "period": "คาบ 3",
            "start": "10:40",
            "end": "11:30"
        },
        {
            "period": "คาบ 4",
            "start": "11:30",
            "end": "12:10"
        },
        {
            "period": "คาบ 5",
            "start": "12:10",
            "end": "13:00"
        },
        {
            "period": "คาบ 6",
            "start": "13:00",
            "end": "13:50"
        },
        {
            "period": "คาบ 7",
            "start": "13:50",
            "end": "14:40"
        },
        {
            "period": "คาบ 8",
            "start": "14:40",
            "end": "15:30"
        },
        {
            "period": "คาบ 9",
            "start": "15:30",
            "end": "16:20"
        }
    ],
    "exam": [
        {
            "period": "เข้าแถว",
            "start": "07:45",
            "end": "08:30"
        },
        {
            "period": "สอบเช้า",
            "start": "08:30",
            "end": "11:30"
        },
        {
            "period": "พักเที่ยง",
            "start": "11:30",
            "end": "13:00"
        },
        {
            "period": "สอบบ่าย",
            "start": "13:00",
            "end": "15:00"
        }
    ]
}


load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host = 'localhost',
        database = 'school_pulse',
        user = os.environ.get('DB_USER'),
        password = os.environ.get('DB_PASS')
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/today')
def get_today_status():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        weekday = date.today().weekday()
        default_assembly = "หน้าห้อง" 
        if weekday in [0, 2, 4]: 
            default_assembly = "เสาธง"
        cur.execute("""
            SELECT assembly_point, schedule_mode, special_message 
            FROM daily_status 
            WHERE status_date = CURRENT_DATE;
        """)
        row = cur.fetchone()

        data = {
            "date": str(date.today()),
            "assembly_point": default_assembly,  # ค่า Default
            "schedule_mode": "normal_50", # ค่า Default
            "special_message": ""
        }

        if row:
            data["assembly_point"] = row[0]
            data["schedule_mode"] = row[1]
            data["special_message"] = row[2]

        
        mode = data["schedule_mode"]
        
        data["timetable"] = SCHEDULE_TEMPLATES.get(mode, SCHEDULE_TEMPLATES["normal_50"])

        data["announcements"] = [] 

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/test')
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({'status': 'seccess', 'database_version': db_version})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0' ,port = 5000)