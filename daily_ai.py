import openai
import json
import os
import datetime

# 从 GitHub Actions 的 Secrets 中读取 API Key
# 这样别人看你的仓库也拿不到你的 Key
api_key = os.getenv("AI_API_KEY") 

client = openai.OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com" # 如果用 OpenAI 改为 https://api.openai.com/v1
)

def generate_questions(count=10):
    prompt = """
    你是一个心理博弈专家。请生成 10 道用于《博弈实验室》游戏的 A/B 选择题。
    要求：JSON 数组格式，字段包含 q, a, b, tag。
    """
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[{"role": "user", "content": prompt}]
    )
    # 解析并返回
    # ... 前面代码保持不变 ...
    raw_content = response.choices[0].message.content
    
    # 增强版解析：只取第一个 [ 和最后一个 ] 之间的内容
    import re
    match = re.search(r'\[.*\]', raw_content, re.DOTALL)
    if match:
        clean_json = match.group()
    else:
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
    
    return json.loads(clean_json)

if __name__ == "__main__":
    try:
        new_data = generate_questions()
        # 写入或更新本地 bank.json
        filename = "bank.json"
        
        # 读取旧数据（如果存在）
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        else:
            old_data = []
            
        # 合并并保存
        combined_data = old_data + new_data
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
        print(f"成功更新题库，当前总题数: {len(combined_data)}")
    except Exception as e:
        print(f"发生错误: {e}")
