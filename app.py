from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from utils.content_generator import (
    generate_teaching_content, 
    generate_exam_questions,
    generate_practice_question,
    analyze_student_answer
)
from utils.data_manager import (
    init_data_files, 
    add_user, 
    find_user,
    add_course,
    get_courses,
    record_usage,
    get_usage_stats,
    add_question,
    get_user_questions,
    get_user_documents,
    save_user_documents
)
from config import get_all_documents
import os
from config import BASE_DIR, USERS_FILE
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'smart_edu_agent_2024'

# 初始化数据文件
init_data_files()

# 读取JSON数据的辅助函数
def read_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

# 创建默认用户
def create_default_users():
    users_data = read_data(USERS_FILE)
    if not any(user.get("username") == "admin" for user in users_data.get("users", [])):
        add_user("admin", "admin123", "admin", "系统管理员")
    if not any(user.get("username") == "teacher1" for user in users_data.get("users", [])):
        add_user("teacher1", "teacher123", "teacher", "张老师")
    if not any(user.get("username") == "student1" for user in users_data.get("users", [])):
        add_user("student1", "student123", "student", "李同学")

create_default_users()

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif session['role'] == 'student':
            return redirect(url_for('student_dashboard'))
        elif session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = find_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['name'] = user['name']
            
            # 记录登录
            record_usage(user['id'], user['role'], 'login')
            
            if user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="用户名或密码错误")
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        record_usage(session['user_id'], session['role'], 'logout')
    session.clear()
    return redirect(url_for('index'))

# 教师端路由
@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    record_usage(session['user_id'], 'teacher', 'access_dashboard')
    courses = get_courses(session['user_id'])
    
    # 获取用户已选文档
    selected_docs = get_user_documents(session['user_id'])
    all_docs = get_all_documents()
    
    return render_template('teacher_dashboard.html', 
                           name=session['name'],
                           courses=courses,
                           selected_docs=selected_docs,
                           all_docs=all_docs)

@app.route('/teacher/generate_content', methods=['POST'])
def generate_teaching_material():
    if 'user_id' not in session or session['role'] != 'teacher':
        return jsonify({"error": "未授权"}), 401
    
    topic = request.json.get('topic')
    if not topic:
        return jsonify({"error": "缺少主题参数"}), 400
    
    record_usage(session['user_id'], 'teacher', 'generate_content')
    content = generate_teaching_content(topic, session['user_id'])
    return jsonify({"content": content})

@app.route('/teacher/generate_exam', methods=['POST'])
def generate_exam():
    if 'user_id' not in session or session['role'] != 'teacher':
        return jsonify({"error": "未授权"}), 401
    
    topic = request.json.get('topic')
    count = request.json.get('count', 5)
    
    if not topic:
        return jsonify({"error": "缺少主题参数"}), 400
    
    record_usage(session['user_id'], 'teacher', 'generate_exam')
    questions = generate_exam_questions(topic, count, session['user_id'])
    return jsonify({"questions": questions})

@app.route('/teacher/save_course', methods=['POST'])
def save_course():
    if 'user_id' not in session or session['role'] != 'teacher':
        return jsonify({"error": "未授权"}), 401
    
    title = request.json.get('title')
    content = request.json.get('content')
    
    if not title or not content:
        return jsonify({"error": "缺少标题或内容"}), 400
    
    course = add_course(session['user_id'], title, content)
    record_usage(session['user_id'], 'teacher', 'save_course')
    return jsonify(course)

# 学生端路由
@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    record_usage(session['user_id'], 'student', 'access_dashboard')
    
    # 获取用户已选文档
    selected_docs = get_user_documents(session['user_id'])
    all_docs = get_all_documents()
    
    return render_template('student_dashboard.html', 
                           name=session['name'],
                           selected_docs=selected_docs,
                           all_docs=all_docs)

@app.route('/student/ask', methods=['POST'])
def student_ask():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({"error": "未授权"}), 401
    
    question = request.json.get('question')
    if not question:
        return jsonify({"error": "缺少问题内容"}), 400
    
    record_usage(session['user_id'], 'student', 'ask_question')
    
    # 调用大模型生成真实答案
    from utils.model_handler import generate_with_context
    answer = generate_with_context(question, session['user_id'])
    
    # 保存问题记录
    add_question(session['user_id'], question, answer)
    
    return jsonify({"answer": answer})

@app.route('/student/questions')
def get_student_questions():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({"error": "未授权"}), 401
    
    questions = get_user_questions(session['user_id'])
    return jsonify(questions)

@app.route('/student/generate_practice', methods=['POST'])
def generate_practice():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({"error": "未授权"}), 401
    
    level = request.json.get('level', 'beginner')
    record_usage(session['user_id'], 'student', 'generate_practice')
    question = generate_practice_question(level, session['user_id'])
    return jsonify({"question": question})

@app.route('/student/submit_answer', methods=['POST'])
def submit_answer():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({"error": "未授权"}), 401
    
    question = request.json.get('question')
    answer = request.json.get('answer')
    
    if not question or not answer:
        return jsonify({"error": "缺少问题或答案"}), 400
    
    record_usage(session['user_id'], 'student', 'submit_answer')
    analysis = analyze_student_answer(question, answer, session['user_id'])
    return jsonify({"analysis": analysis})

# 管理端路由
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    record_usage(session['user_id'], 'admin', 'access_dashboard')
    stats = get_usage_stats()
    return render_template('admin_dashboard.html', 
                           name=session['name'],
                           stats=stats)

# 文档管理路由
@app.route('/documents')
def document_manager():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取所有可用文档
    all_docs = get_all_documents()
    
    # 获取用户已选文档
    selected_docs = get_user_documents(session['user_id'])
    
    return render_template('document_manager.html', 
                           name=session['name'],
                           all_docs=all_docs,
                           selected_docs=selected_docs)

@app.route('/update_documents', methods=['POST'])
def update_documents():
    if 'user_id' not in session:
        return jsonify({"error": "未授权"}), 401
    
    selected_docs = request.json.get('selected_docs', [])
    save_user_documents(session['user_id'], selected_docs)
    
    return jsonify({"status": "success", "selected_docs": selected_docs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)