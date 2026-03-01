import requests

headers = {
    "Autorization" : "Bearer: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY5OTgxMzE5fQ.bjvFlmyixMfRQ4X1N-vK6oOKWARIimTt24d9eePR1Fk"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)

print(requisicao.json)