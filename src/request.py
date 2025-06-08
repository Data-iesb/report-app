import requests

url = "https://hewx1kjfxh.execute-api.us-east-1.amazonaws.com/prod/dataiesb-auth"

payload = {
    "username": "your_username",
    "password": "your_password"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)

    # If response is JSON
    if "application/json" in response.headers.get("Content-Type", ""):
        data = response.json()
        print("Response JSON:", data)
    else:
        print("Response Text:", response.text)

except requests.exceptions.RequestException as e:
    print("Request failed:", e)

