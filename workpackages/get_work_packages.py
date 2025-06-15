import requests
from utils.excel_utils import write_work_packages_to_excel
from endpoints.endpoints import get_work_packages_list_endpoint

def extract_id_from_link(link):
    href = link.get("href") if link else None
    if href:
        return href.split("/")[-1]
    return None

def fetch_all_work_packages(openproject_url, headers, page_size=100):
    """
    Fetch all work packages from the OpenProject API, handling pagination.
    Returns a list of dicts with required fields for Excel export.
    """
    all_packages = []
    offset = 1
    while True:
        url = get_work_packages_list_endpoint(openproject_url, offset=offset, page_size=page_size)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch work packages: {resp.status_code}")
            break
        data = resp.json()
        elements = data.get("_embedded", {}).get("elements", [])
        for wp in elements:
            all_packages.append({
                "work_package_id": wp.get("id"),
                "subject": wp.get("subject"),
                "project_id": extract_id_from_link(wp.get("_links", {}).get("project")),
                "author_id": extract_id_from_link(wp.get("_links", {}).get("author")),
                "type_id": extract_id_from_link(wp.get("_links", {}).get("type")),
                "status_id": extract_id_from_link(wp.get("_links", {}).get("status")),
                "priority_id": extract_id_from_link(wp.get("_links", {}).get("priority")),
                "assignee_id": extract_id_from_link(wp.get("_links", {}).get("assignee")),
                "category_id": extract_id_from_link(wp.get("_links", {}).get("category")),
                "start_date": wp.get("startDate"),
                "due_date": wp.get("dueDate"),
                "duration": wp.get("duration"),
                "description": wp.get("description", {}).get("raw") if isinstance(wp.get("description"), dict) else wp.get("description"),
                "lock_version": wp.get("lockVersion"),
                "parent_id": extract_id_from_link(wp.get("_links", {}).get("parent")),
            })
        total = data.get("total", 0)
        count = data.get("count", 0)
        if offset + count > total:
            break
        offset += count
    return all_packages

def export_work_packages_to_excel(openproject_url, headers, excel_file="workpackages.xlsx"):
    work_packages = fetch_all_work_packages(openproject_url, headers)
    write_work_packages_to_excel(work_packages, excel_file)
    print(f"✅ Exported {len(work_packages)} work packages to {excel_file}")
