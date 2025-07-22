import json
import os
from datetime import datetime
from config import (
    USERS_FILE, COURSES_FILE, EXERCISES_FILE, 
    USAGE_FILE, QUESTIONS_FILE, DOCUMENTS_FILE,
    FAVORITES_FILE
)
def init_data_files():
    """初始化数据文件"""
    data_files = {
        USERS_FILE: {"users": []},
        COURSES_FILE: {"courses": []},
        EXERCISES_FILE: {"exercises": []},
        USAGE_FILE: {"teacher_usage": [], "student_usage": []},
        QUESTIONS_FILE: {"questions": []},
        DOCUMENTS_FILE: {"documents": []},
        FAVORITES_FILE: {"favorites": []}
    }
    
    for file, default_data in data_files.items():
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump(default_data, f, indent=2)


def read_data(file_path):
    """读取JSON数据"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r') as f:
        return json.load(f)

def write_data(file_path, data):
    """写入JSON数据"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_user(username, password, role, name=""):
    """添加用户"""
    users_data = read_data(USERS_FILE)
    new_user = {
        "id": len(users_data["users"]) + 1,
        "username": username,
        "password": password,  # 实际应用中应加密存储
        "role": role,
        "name": name,
        "created_at": datetime.now().isoformat()
    }
    users_data["users"].append(new_user)
    write_data(USERS_FILE, users_data)
    return new_user

def find_user(username, password):
    """查找用户"""
    users_data = read_data(USERS_FILE)
    for user in users_data["users"]:
        if user["username"] == username and user["password"] == password:
            return user
    return None

def add_course(teacher_id, title, content):
    """添加课程"""
    courses_data = read_data(COURSES_FILE)
    new_course = {
        "id": len(courses_data["courses"]) + 1,
        "teacher_id": teacher_id,
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat()
    }
    courses_data["courses"].append(new_course)
    write_data(COURSES_FILE, courses_data)
    return new_course

def get_courses(teacher_id=None):
    """获取课程列表"""
    courses_data = read_data(COURSES_FILE)
    if teacher_id:
        return [c for c in courses_data["courses"] if c["teacher_id"] == teacher_id]
    return courses_data["courses"]

def record_usage(user_id, role, action):
    """记录使用情况"""
    usage_data = read_data(USAGE_FILE)
    usage_record = {
        "user_id": user_id,
        "role": role,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }
    
    if role == "teacher":
        usage_data["teacher_usage"].append(usage_record)
    else:
        usage_data["student_usage"].append(usage_record)
    
    write_data(USAGE_FILE, usage_data)

def get_usage_stats():
    """获取使用统计"""
    usage_data = read_data(USAGE_FILE)
    
    # 今日日期
    today = datetime.now().date().isoformat()
    
    # 教师使用统计
    teacher_today = [u for u in usage_data["teacher_usage"] 
                    if datetime.fromisoformat(u["timestamp"]).date().isoformat() == today]
    teacher_actions = [u["action"] for u in teacher_today]
    
    # 学生使用统计
    student_today = [u for u in usage_data["student_usage"] 
                    if datetime.fromisoformat(u["timestamp"]).date().isoformat() == today]
    student_actions = [u["action"] for u in student_today]
    
    return {
        "teacher": {
            "today_count": len(teacher_today),
            "top_actions": max(set(teacher_actions), key=teacher_actions.count) if teacher_actions else "无"
        },
        "student": {
            "today_count": len(student_today),
            "top_actions": max(set(student_actions), key=student_actions.count) if student_actions else "无"
        }
    }

def add_question(user_id, question, answer):
    """添加问题记录"""
    questions_data = read_data(QUESTIONS_FILE)
    new_question = {
        "id": len(questions_data["questions"]) + 1,
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }
    questions_data["questions"].append(new_question)
    write_data(QUESTIONS_FILE, questions_data)
    return new_question

def get_user_questions(user_id):
    """获取用户的问题记录"""
    questions_data = read_data(QUESTIONS_FILE)
    return [q for q in questions_data["questions"] if q["user_id"] == user_id]

def get_document_settings():
    """获取文档配置"""
    if not os.path.exists(DOCUMENTS_FILE):
        return {"documents": []}

    with open(DOCUMENTS_FILE, 'r') as f:
        return json.load(f)

def update_document_settings(settings):
    """更新文档配置"""
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def get_user_documents(user_id):
    """获取用户选择的文档"""
    doc_settings = get_document_settings()
    for doc in doc_settings.get("documents", []):
        if doc["user_id"] == user_id:
            return doc["selected_docs"]
    return []

def save_user_documents(user_id, selected_docs):
    """保存用户选择的文档"""
    doc_settings = get_document_settings()
    updated = False
    
    # 更新现有用户配置
    for doc in doc_settings.get("documents", []):
        if doc["user_id"] == user_id:
            doc["selected_docs"] = selected_docs
            updated = True
            break
    
    # 添加新用户配置
    if not updated:
        doc_settings.setdefault("documents", []).append({
            "user_id": user_id,
            "selected_docs": selected_docs
        })
    
    update_document_settings(doc_settings)

def add_favorite_question(user_id, question_id, source, question_text=None):
    """添加收藏题目"""
    favorites_data = read_data(FAVORITES_FILE)
    new_favorite = {
        "id": len(favorites_data["favorites"]) + 1,
        "user_id": user_id,
        "question_id": question_id,
        "question": question_text or f"题目 {question_id}",
        "source": source,  # "practice"或"exam"
        "timestamp": datetime.now().isoformat()
    }
    favorites_data["favorites"].append(new_favorite)
    write_data(FAVORITES_FILE, favorites_data)
    return new_favorite

def get_favorite_questions(user_id):
    """获取用户的收藏题目列表"""
    favorites_data = read_data(FAVORITES_FILE)
    questions_data = read_data(QUESTIONS_FILE)
    
    favorites = []
    for fav in favorites_data["favorites"]:
        if fav["user_id"] == user_id:
            # 查找对应的完整问题信息
            question_info = next(
                (q for q in questions_data["questions"] 
                 if str(q["id"]) == str(fav["question_id"])),
                None
            )
            
            if question_info:
                favorite = {
                    "id": fav["id"],
                    "question_id": fav["question_id"],
                    "question": question_info["question"],
                    "answer": question_info["answer"],
                    "source": fav["source"],
                    "timestamp": fav["timestamp"]
                }
            else:
                # 如果找不到问题信息，使用收藏中的基本信息
                favorite = {
                    "id": fav["id"],
                    "question_id": fav["question_id"],
                    "question": fav.get("question", "未知题目"),
                    "answer": "题目信息不可用",
                    "source": fav["source"],
                    "timestamp": fav["timestamp"]
                }
            favorites.append(favorite)
    
    return favorites

def delete_favorite_question(user_id, favorite_id):
    """删除收藏题目"""
    try:
        favorites_data = read_data(FAVORITES_FILE)
        original_count = len(favorites_data["favorites"])
        
        # 确保favorite_id类型一致
        favorite_id = int(favorite_id) if isinstance(favorite_id, str) else favorite_id
        
        favorites_data["favorites"] = [
            fav for fav in favorites_data["favorites"]
            if not (fav["user_id"] == user_id and fav["id"] == favorite_id)
        ]
        
        write_data(FAVORITES_FILE, favorites_data)
        
        deleted_count = original_count - len(favorites_data["favorites"])
        return {
            "status": "success" if deleted_count > 0 else "not_found",
            "deleted_count": deleted_count
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }