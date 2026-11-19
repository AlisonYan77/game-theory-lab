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
    你是一个心理博弈专家。请生成 10 道用于《博弈实验室》游戏的中文 A/B 选择题。
    严格要求：输出 JSON 数组，每题只包含三个字段：q (题干), a (选项A), b (选项B)。
    不要输出其他任何字段名，不要输出英文，不要输出注释。
    示例：[{"q": "...", "a": "...", "b": "..."}]
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
            
        # 入库前校验：只保留 {q, a, b} 齐全且字段为字符串的题，过滤 AI 输出漂移
        valid = [q for q in new_data
                 if isinstance(q, dict)
                 and all(isinstance(q.get(k), str) and q.get(k).strip() for k in ('q', 'a', 'b'))]
        # 只保留 q/a/b 三个字段，丢弃多余字段
        valid = [{'q': q['q'].strip(), 'a': q['a'].strip(), 'b': q['b'].strip()} for q in valid]
        print(f"本次生成 {len(new_data)} 题，校验通过 {len(valid)} 题")
        # 与已有题库去重（按题干）
        existing_qs = {q.get('q') for q in old_data if isinstance(q, dict)}
        valid = [q for q in valid if q['q'] not in existing_qs]
        # 合并并保存
        combined_data = old_data + valid
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
        print(f"成功更新题库，当前总题数: {len(combined_data)}")
    except Exception as e:
        print(f"发生错误: {e}")