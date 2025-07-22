import os
import glob

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-959db6c460bb4ace9a066bd4c065981e"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 数据存储路径
DATA_PATH = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_PATH, "users.json")
COURSES_FILE = os.path.join(DATA_PATH, "courses.json")
EXERCISES_FILE = os.path.join(DATA_PATH, "exercises.json")
USAGE_FILE = os.path.join(DATA_PATH, "usage.json")
QUESTIONS_FILE = os.path.join(DATA_PATH, "questions.json")
DOCUMENTS_FILE = os.path.join(DATA_PATH, "documents.json")
FAVORITES_FILE = os.path.join(DATA_PATH, "favorites.json")  # 收藏题目数据文件

# 知识库路径
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "knowledge_base")

# 系统角色
ROLES = ["admin", "teacher", "student"]

# 获取知识库中所有文档
def get_all_documents():
    """获取知识库中所有文档列表"""
    doc_files = glob.glob(os.path.join(KNOWLEDGE_BASE_PATH, "*.docx"))
    return [os.path.basename(doc) for doc in doc_files]