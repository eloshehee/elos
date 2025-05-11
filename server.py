from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database initialization
def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    
    # Create classes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database when server starts
init_db()

# API Routes
@app.route('/api/classes', methods=['GET'])
def get_classes():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute('SELECT * FROM classes')
    classes = [{'id': row[0], 'name': row[1], 'number': row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(classes)

@app.route('/api/classes', methods=['POST'])
def add_class():
    data = request.json
    name = data.get('name')
    number = data.get('number')
    
    if not name or not number:
        return jsonify({'success': False, 'error': 'Name and number are required'}), 400
    
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute('INSERT INTO classes (name, number) VALUES (?, ?)', (name, number))
    conn.commit()
    class_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'id': class_id})

@app.route('/api/students', methods=['GET'])
def get_students():
    class_id = request.args.get('class_id')
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    
    if class_id:
        c.execute('SELECT * FROM students WHERE class_id = ?', (class_id,))
    else:
        c.execute('SELECT * FROM students')
    
    students = [{'id': row[0], 'class_id': row[1], 'name': row[2], 'student_id': row[3], 'gender': row[4]} 
               for row in c.fetchall()]
    conn.close()
    return jsonify(students)

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    class_id = data.get('class_id')
    name = data.get('name')
    student_id = data.get('student_id')
    gender = data.get('gender')
    
    if not all([class_id, name, student_id, gender]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute('INSERT INTO students (class_id, name, student_id, gender) VALUES (?, ?, ?, ?)',
              (class_id, name, student_id, gender))
    conn.commit()
    student_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'id': student_id})

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 