import requests

resp = requests.get('http://localhost:8080/api/team/list')
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Team: {data['team']['name']}")
print(f"Agents: {len(data['team']['agents'])}")
for agent in data['team']['agents']:
    print(f"  - {agent['id']}: {agent['name']} ({agent['model']})")
