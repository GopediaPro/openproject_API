from requester.requester import post_request
from utils.excel_utils import read_users_from_excel
from group.group import get_group_list, print_group_list_with_index, update_group_members

def create_user(api_endpoint, user_payload, headers):
    """
    OpenProject에 단일 사용자 생성
    """
    response = post_request(api_endpoint, user_payload, headers)
    return response

def bulk_create_users(api_endpoint, headers, excel_file, group_api_endpoint=None):
    """
    엑셀에서 사용자 생성 후, 그룹 선택 및 그룹에 사용자 추가
    """
    try:
        users = read_users_from_excel(excel_file)
    except Exception as e:
        print(f"❌ 엑셀 읽기 오류: {e}")
        return

    group_id = None
    if group_api_endpoint:
        # 그룹 목록 조회 및 선택
        groups = get_group_list(group_api_endpoint, headers)
        if not groups:
            print("그룹 목록을 불러올 수 없습니다. 그룹 추가 없이 진행합니다.")
        else:
            print("\n[그룹 목록]")
            print_group_list_with_index(groups)
            group_elements = groups["_embedded"]["elements"]
            try:
                sel = int(input("사용자를 추가할 그룹 번호를 선택하세요 (건너뛰려면 0): "))
                if sel > 0 and sel <= len(group_elements):
                    group_id = group_elements[sel-1]["id"]
                else:
                    print("그룹 추가 없이 사용자만 생성합니다.")
            except Exception:
                print("입력 오류. 그룹 추가 없이 사용자만 생성합니다.")

    created_user_ids = []
    for user in users:
        response = create_user(api_endpoint, user, headers)
        if response is not None and response.status_code == 201:
            print(f"✅ 사용자 생성 성공: {user['login']}")
            user_id = response.json().get("id")
            if user_id:
                created_user_ids.append(user_id)
        else:
            print(f"❌ 사용자 생성 실패: {user['login']} - {response.status_code if response is not None else 'No Response'}")

    # 그룹에 사용자 추가
    if group_id and created_user_ids:
        group_update_resp = update_group_members(group_api_endpoint, group_id, created_user_ids, headers)
        if group_update_resp is not None and group_update_resp.status_code in (200, 204):
            print(f"✅ 그룹(id={group_id})에 사용자 추가 성공!")
        else:
            print(f"❌ 그룹에 사용자 추가 실패: {group_update_resp.status_code if group_update_resp is not None else 'No Response'}") 