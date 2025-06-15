import requests

def create_work_package(api_endpoint, payload, headers):
    """
    OpenProject Work Package 생성 함수
    :param api_endpoint: work_packages API endpoint (e.g., https://.../api/v3/work_packages)
    :param payload: work package 생성에 필요한 dict (JSON 구조)
    :param headers: 인증 및 Content-Type 헤더
    :return: response 객체
    """
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return None 