import requests

def post_request(url, payload, headers):
    """
    POST 요청 래퍼
    """
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
        return None 