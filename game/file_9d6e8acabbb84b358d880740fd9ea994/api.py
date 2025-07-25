import requests

# URL API
url = "http://127.0.0.1:8000/games/API/leaderboard/"

# Dữ liệu gửi lên
data = {
    "games": 115,
    "users": 1,
    "score": 99999999
}

# Lấy CSRF token từ trang Django
session = requests.Session()
csrf_token = session.get("http://127.0.0.1:8000/").cookies.get("csrftoken")  # URL trang Django

# Headers với CSRF token
headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token  # Thêm CSRF token
}

# Gửi request POST
response = session.post(url, json=data, headers=headers)

# Kiểm tra phản hồi
if response.status_code == 200:
    print("Gửi điểm thành công:", response.json())
else:
    print(f"Lỗi {response.status_code}: {response.text}")
