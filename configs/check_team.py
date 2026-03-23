import json

with open('team.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Name:', data['name'])
print('Agents:', len(data['agents']))
for a in data['agents']:
    print(f"  {a['id']}: {a['name']}")
