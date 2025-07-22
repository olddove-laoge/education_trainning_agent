from utils.model_handler import generate_with_context
import markdown
import re

def generate_teaching_content(topic, user_id=None):
    """生成教学内容"""
    prompt = f"""
    根据知识库内容，为主题'{topic}'设计一个完整的教学方案，包含以下部分：
    
    1. 教学目标（清晰明确）
    2. 知识讲解（分3-5个核心知识点，每个知识点详细解释）
    3. 实训练习（2-3个与知识点相关的实践练习）
    4. 时间分配建议（总时长45分钟）
    5. 教学资源建议（推荐相关学习资源）
    
    输出格式使用Markdown，包含标题、列表和必要的代码块（如果是技术类内容）。
    """
    return markdown.markdown(generate_with_context(prompt, user_id, max_tokens=2000))

def generate_exam_questions(topic, count=5, user_id=None):
    """生成考核题目"""
    prompt = f"""
    根据知识库内容，为主题'{topic}'生成{count}道考核题目，要求：
    
    1. 题目类型多样化（选择题、填空题、简答题）
    2. 每道题目标注难度（简单/中等/困难）
    3. 包含参考答案和详细解析
    4. 如果是编程题，提供示例代码
    
    输出格式使用Markdown，题目和答案分开。
    """
    return markdown.markdown(generate_with_context(prompt, user_id))

def generate_practice_question(student_level="beginner", user_id=None):
    """生成练习题"""
    prompt = f"""
    根据知识库内容，为{student_level}水平的学生生成一道练习题：
    
    1. 题目清晰明确
    2. 提供解题思路提示
    3. 包含参考答案和解析
    
    输出格式使用Markdown。
    """
    return markdown.markdown(generate_with_context(prompt, user_id))

def analyze_student_answer(question, answer, user_id=None):
    """分析学生答案"""
    prompt = f"""
    作为教学助手，请分析以下学生答案：
    
    题目: {question}
    学生答案: {answer}
    
    请提供：
    1. 答案正确性评估（正确/部分正确/错误）
    2. 错误点分析（如果有错误）
    3. 改进建议
    4. 相关知识点的复习建议
    
    输出格式使用Markdown。
    """
    return markdown.markdown(generate_with_context(prompt, user_id))