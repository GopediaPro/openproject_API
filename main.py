import os
import typer
from dotenv import load_dotenv
from auth.auth import get_auth_headers
from users.create_user import create_user, bulk_create_users
from workpackages.create_work_package import create_work_package
from datetime import datetime

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

@app.command("create-work-package")
def create_work_package_cmd(
    subject: str = typer.Option(..., help="Work package subject"),
    project_id: int = typer.Option(..., help="Project ID (e.g., 3)"),
    type_id: int = typer.Option(1, help="Type ID (e.g., 1 for Task)"),
    status_id: int = typer.Option(1, help="Status ID (e.g., 1 for New)"),
    priority_id: int = typer.Option(9, help="Priority ID (e.g., 9 for Normal)"),
    author_id: int = typer.Option(..., help="Author user ID"),
    assignee_id: int = typer.Option(None, help="Assignee user ID (optional)"),
    category_id: int = typer.Option(None, help="Category ID (optional)"),
    start_date: str = typer.Option(None, help="Start date (YYYY-MM-DD, optional)"),
    due_date: str = typer.Option(None, help="Due date (YYYY-MM-DD, optional)"),
    description: str = typer.Option("", help="Description (optional)")
):
    """Create a single work package"""
    openproject_url, headers = get_env()
    api_endpoint = f"{openproject_url}/api/v3/work_packages"

    # duration 계산
    duration = None
    if start_date and due_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            due_dt = datetime.strptime(due_date, "%Y-%m-%d")
            days = (due_dt - start_dt).days + 1
            duration = f"P{days}D"
        except Exception as e:
            print(f"❌ 날짜 형식 오류: {e}")
            return

    payload = {
        "subject": subject,
        "scheduleManually": True,
        "startDate": start_date,
        "dueDate": due_date,
        "duration": duration,
        "_links": {
            "category": {"href": f"/api/v3/categories/{category_id}"} if category_id else None,
            "type": {"href": f"/api/v3/types/{type_id}"},
            "priority": {"href": f"/api/v3/priorities/{priority_id}"},
            "project": {"href": f"/api/v3/projects/{project_id}"},
            "status": {"href": f"/api/v3/statuses/{status_id}"},
            "author": {"href": f"/api/v3/users/{author_id}"},
            "assignee": {"href": f"/api/v3/users/{assignee_id}"} if assignee_id else None,
        },
        "description": {"raw": description}
    }
    # _links에서 None 값 제거
    payload["_links"] = {k: v for k, v in payload["_links"].items() if v is not None}
    # payload에서 None 값 제거
    payload = {k: v for k, v in payload.items() if v is not None}

    response = create_work_package(api_endpoint, payload, headers)
    if response is not None and response.status_code == 201:
        print("✅ Work package 생성 성공!")
        print(response.json())
    else:
        print(f"❌ Work package 생성 실패: {response.status_code if response is not None else 'No Response'}")
        if response is not None:
            print(response.text)

if __name__ == "__main__":
    app()
