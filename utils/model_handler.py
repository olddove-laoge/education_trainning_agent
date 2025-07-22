from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME
from utils.docx_reader import read_selected_docs
import time
from utils.data_manager import get_user_documents

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def generate_with_context(prompt, user_id=None, max_tokens=1500):
    """使用知识库上下文生成内容"""
    system_msg = "你是一个专业教学助手，请根据提供的知识库内容回答问题"
    
    # 获取用户选择的文档
    if user_id:
        selected_docs = get_user_documents(user_id)
    else:
        selected_docs = []
    
    # 获取知识库内容（限制长度）
    knowledge = read_selected_docs(selected_docs, 4000)  # 限制为4000字符
    
    # 构建系统消息
    system_content = f"{system_msg}\n\n知识库内容:\n{knowledge}" if knowledge else system_msg
    
    # 添加用户提示的上下文
    user_content = prompt
    
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            max_tokens=max_tokens,
            stream=False
        )
        content = response.choices[0].message.content
        latency = time.time() - start_time
        print(f"模型调用耗时: {latency:.2f}秒, 生成内容长度: {len(content)}")
        return content
    except Exception as e:
        print(f"模型调用出错: {str(e)}")
        return f"生成内容时出错: {str(e)}"