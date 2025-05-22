import requests

url = "http://localhost:5000/bot/submit"
files = {'file': open("bot2.py", "rb")}
data = {'team_id': 1}

res = requests.post(url, files=files, data=data)
print(res.json())
