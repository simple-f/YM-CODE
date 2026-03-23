import json

# 读取原始字节
with open('team.json', 'rb') as f:
    raw = f.read()

# 尝试解码
try:
    text = raw.decode('utf-8')
    # 检查是否乱码
    if 'ȫ' in text or '' in text:
        print("Detected garbled text")
        # 可能是 UTF-8 被当作 Latin-1/CP1252 保存后再编码成 UTF-8
        # 尝试反向操作
        try:
            # 先解码成 UTF-8 字节，再当作 Latin-1 解码，再编码成 UTF-8
            fixed = text.encode('latin-1').decode('utf-8')
            print("Fixed with latin-1 roundtrip")
            text = fixed
        except:
            try:
                fixed = text.encode('cp1252').decode('utf-8')
                print("Fixed with cp1252 roundtrip")
                text = fixed
            except:
                print("Could not fix encoding")
    
    # 保存修复后的文件
    with open('team_fixed.json', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Saved to team_fixed.json")
    
    # 验证
    with open('team_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Fixed name:", data['name'])
    
except Exception as e:
    print(f"Error: {e}")
