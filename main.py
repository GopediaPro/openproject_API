import os
import typer
from dotenv import load_dotenv
from auth.auth import get_auth_headers
from users.create_user import create_user, bulk_create_users
from workpackages.create_work_package import create_work_package, bulk_create_work_packages, bulk_patch_work_package_parents
from datetime import datetime
from endpoints.endpoints import get_user_endpoint, get_group_endpoint, get_work_package_endpoint
from payloads.user_payloads import build_user_payload
from payloads.work_package_payload import build_work_package_payload
from utils.excel_utils import read_work_packages_from_excel, read_parent_patch_from_excel

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
    api_endpoint = get_user_endpoint(openproject_url)
    group_api_endpoint = get_group_endpoint(openproject_url)
    user_payload = build_user_payload(login, email, first_name, last_name, password)
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
    api_endpoint = get_user_endpoint(openproject_url)
    group_api_endpoint = get_group_endpoint(openproject_url)
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
    api_endpoint = get_work_package_endpoint(openproject_url)

    payload = build_work_package_payload(
        subject=subject,
        project_id=project_id,
        type_id=type_id,
        status_id=status_id,
        priority_id=priority_id,
        author_id=author_id,
        assignee_id=assignee_id,
        category_id=category_id,
        start_date=start_date,
        due_date=due_date,
        description=description
    )

    response = create_work_package(api_endpoint, payload, headers)
    if response is not None and response.status_code == 201:
        print("✅ Work package 생성 성공!")
        print(response.json())
    else:
        print(f"❌ Work package 생성 실패: {response.status_code if response is not None else 'No Response'}")
        if response is not None:
            print(response.text)

@app.command("bulk-create-work-packages")
def bulk_create_work_packages_cmd():
    """Create multiple work packages from workpackages.xlsx"""
    openproject_url, headers = get_env()
    api_endpoint = get_work_package_endpoint(openproject_url)
    excel_file = "workpackages.xlsx"
    try:
        work_packages_data = read_work_packages_from_excel(excel_file)
    except Exception as e:
        print(f"❌ Excel 파일 읽기 오류: {e}")
        return
    payloads = [
        build_work_package_payload(
            subject=wp["subject"],
            project_id=wp["project_id"],
            type_id=wp.get("type_id", 1),
            status_id=wp.get("status_id", 1),
            priority_id=wp.get("priority_id", 9),
            author_id=wp["author_id"],
            assignee_id=wp.get("assignee_id"),
            category_id=wp.get("category_id"),
            start_date=wp.get("start_date"),
            due_date=wp.get("due_date"),
            description=wp.get("description", "")
        ) for wp in work_packages_data
    ]
    responses = bulk_create_work_packages(api_endpoint, headers, payloads)
    for idx, resp in enumerate(responses):
        if resp is not None and resp.status_code == 201:
            print(f"✅ {idx+1}번째 Work package 생성 성공!")
        else:
            print(f"❌ {idx+1}번째 Work package 생성 실패: {resp.status_code if resp is not None else 'No Response'}")
            if resp is not None:
                print(resp.text)

@app.command("bulk-patch-work-package-parents")
def bulk_patch_work_package_parents_cmd(
    excel: str = typer.Option("parent_patches.xlsx", help="Path to Excel file with parent patch info")
):
    """Bulk patch work package parents from Excel (work_package_id, lock_version, parent_id)"""
    openproject_url, headers = get_env()
    try:
        parent_patches = read_parent_patch_from_excel(excel)
    except Exception as e:
        print(f"❌ Excel 파일 읽기 오류: {e}")
        return
    responses = bulk_patch_work_package_parents(openproject_url, headers, parent_patches)
    for idx, resp in enumerate(responses):
        patch = parent_patches[idx]
        if resp is not None and resp.status_code in (200, 201):
            print(f"✅ {idx+1}번째 parent patch 성공 (work_package_id={patch['work_package_id']})!")
        else:
            print(f"❌ {idx+1}번째 parent patch 실패 (work_package_id={patch['work_package_id']}): {resp.status_code if resp is not None else 'No Response'}")
            if resp is not None:
                print(resp.text)

if __name__ == "__main__":
    app()
