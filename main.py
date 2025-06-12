import os
import typer
from dotenv import load_dotenv
from auth.auth import get_auth_headers
from users.create_user import create_user, bulk_create_users

def get_env():
    load_dotenv()
    openproject_url = os.getenv("OPENPROJECT_URL")
    api_key = os.getenv("OPENPROJECT_API_KEY")
    headers = get_auth_headers(api_key)
    return openproject_url, headers

app = typer.Typer()

@app.command("create-user")
def create_user_cmd(
    login: str = typer.Option(..., help="User login"),
    email: str = typer.Option(..., help="User email"),
    first_name: str = typer.Option(..., help="First name"),
    last_name: str = typer.Option(..., help="Last name"),
    password: str = typer.Option(..., help="Password"),
    group_id: int = typer.Option(None, help="Group ID to add user to (optional)")
):
    """Create a single user (optionally add to group)"""
    openproject_url, headers = get_env()
    api_endpoint = f"{openproject_url}/api/v3/users"
    group_api_endpoint = f"{openproject_url}/api/v3/groups"
    user_payload = {
        "login": login,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "password": password,
        "admin": False,
        "status": "active"
    }
    response = create_user(api_endpoint, user_payload, headers)
    if response is not None and response.status_code == 201:
        print("✅ 사용자 생성 성공!")
        user_id = response.json().get("id")
        if group_id and user_id:
            from group.group import update_group_members
            group_update_resp = update_group_members(group_api_endpoint, group_id, [user_id], headers)
            if group_update_resp is not None and group_update_resp.status_code in (200, 204):
                print(f"✅ 그룹(id={group_id})에 사용자 추가 성공!")
            else:
                print(f"❌ 그룹에 사용자 추가 실패: {group_update_resp.status_code if group_update_resp is not None else 'No Response'}")
    else:
        print(f"❌ 사용자 생성 실패: {response.status_code if response is not None else 'No Response'}")

@app.command("bulk-create-users")
def bulk_create_users_cmd(
    excel: str = typer.Option(..., help="Path to Excel file"),
    group_id: int = typer.Option(None, help="Group ID to add users to (optional)")
):
    """Create multiple users from Excel (optionally add to group)"""
    openproject_url, headers = get_env()
    api_endpoint = f"{openproject_url}/api/v3/users"
    group_api_endpoint = f"{openproject_url}/api/v3/groups"
    # group_id가 있으면 group_api_endpoint를 넘기고, 없으면 기존 로직(선택) 유지
    if group_id:
        # group_id를 바로 넘기기 위해 bulk_create_users를 약간 수정해야 할 수도 있음
        # 여기서는 group_id를 넘기고, 내부에서 바로 추가하도록 처리
        bulk_create_users(api_endpoint, headers, excel, group_api_endpoint=group_api_endpoint, force_group_id=group_id)
    else:
        bulk_create_users(api_endpoint, headers, excel, group_api_endpoint=group_api_endpoint)

if __name__ == "__main__":
    app()
