from requester.requester import post_request
import requests

def get_group_list(api_endpoint, headers):
    """
    /api/v3/groups GET: 그룹 목록 반환
    """
    try:
        response = requests.get(api_endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()  # groups 데이터
        else:
            print(f"❌ 그룹 목록 조회 실패: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 네트워크 오류: {e}")
        return None

def update_group_members(api_endpoint, group_id, user_ids, headers, group_name=None):
    """
    /api/v3/groups/{id} PATCH: 그룹 멤버 업데이트
    user_ids: [42, 43, ...]
    group_name: 변경할 그룹명 (없으면 기존 이름 유지)
    """
    url = f"{api_endpoint}/{group_id}"
    members_links = [{"href": f"/api/v3/users/{uid}"} for uid in user_ids]
    data = {"_links": {"members": members_links}}
    if group_name:
        data["name"] = group_name
    try:
        response = requests.patch(url, headers=headers, json=data)
        return response
    except Exception as e:
        print(f"❌ 네트워크 오류: {e}")
        return None

def print_group_list_with_index(groups):
    """
    그룹 목록을 번호와 함께 출력
    """
    if not groups or "_embedded" not in groups or "elements" not in groups["_embedded"]:
        print("그룹 데이터가 없습니다.")
        return
    for idx, group in enumerate(groups["_embedded"]["elements"], 1):
        print(f"{idx}. {group['name']} (id: {group['id']})") 