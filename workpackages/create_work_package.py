import requests
import pandas as pd

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

def bulk_create_work_packages(api_endpoint, headers, work_packages, excel_file=None):
    """
    여러 개의 work package를 생성하는 함수
    :param api_endpoint: work_packages API endpoint
    :param headers: 인증 및 Content-Type 헤더
    :param work_packages: work package payload dict의 리스트
    :param excel_file: 원본 엑셀 파일 경로 (id, lockVersion 기록용, 선택)
    :return: 각 work package 생성 결과 리스트
    """
    results = []
    ids = []
    lock_versions = []
    for payload in work_packages:
        resp = create_work_package(api_endpoint, payload, headers)
        results.append(resp)
        if resp is not None and resp.status_code == 201:
            data = resp.json()
            ids.append(data.get("id"))
            lock_versions.append(data.get("lockVersion"))
        else:
            ids.append(None)
            lock_versions.append(None)
    # 엑셀 파일에 결과 기록
    if excel_file is not None:
        try:
            df = pd.read_excel(excel_file)
            df["work_package_id"] = ids
            df["lock_version"] = lock_versions
            df.to_excel(excel_file, index=False)
        except Exception as e:
            print(f"❌ 엑셀 파일에 결과 기록 실패: {e}")
    return results

def bulk_patch_work_package_parents(openproject_url, headers, parent_patches):
    """
    여러 work package의 parent를 PATCH로 설정하는 함수
    :param openproject_url: OpenProject base URL
    :param headers: 인증 및 Content-Type 헤더
    :param parent_patches: dict 리스트 (work_package_id, lock_version, parent_id)
    :return: 각 patch 결과 리스트
    """
    results = []
    for patch in parent_patches:
        work_package_id = patch["work_package_id"]
        lock_version = patch["lock_version"]
        parent_id = patch["parent_id"]
        url = f"{openproject_url}/api/v3/work_packages/{work_package_id}"
        from payloads.work_package_payload import build_parent_patch_payload
        payload = build_parent_patch_payload(lock_version, parent_id)
        try:
            resp = requests.patch(url, headers=headers, json=payload)
            results.append(resp)
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류 (work_package_id={work_package_id}): {e}")
            results.append(None)
    return results 