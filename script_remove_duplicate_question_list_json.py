import json
json_path = "question_list.json"

with open(json_path, 'r') as f:
    d = json.load(f)

with open(json_path, 'w', encoding='utf-8') as f:
    d = {k: v if isinstance(v, set) else [v] for k, v in d.items()}
    json.dump(d, f, ensure_ascii=False)
