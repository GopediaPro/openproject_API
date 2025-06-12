import base64

def get_auth_headers(api_key):
    """
    API 키로 인증 헤더 생성
    """
    auth_string = f"apikey:{api_key}".encode("utf-8")
    encoded_auth = base64.b64encode(auth_string).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    return headers 