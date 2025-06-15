def build_work_package_payload(subject, project_id, type_id=1, status_id=1, priority_id=9, author_id=None, assignee_id=None, category_id=None, start_date=None, due_date=None, description=""):
    from datetime import datetime
    duration = None
    if start_date and due_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            due_dt = datetime.strptime(due_date, "%Y-%m-%d")
            days = (due_dt - start_dt).days + 1
            duration = f"P{days}D"
        except Exception:
            duration = None
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
            "author": {"href": f"/api/v3/users/{author_id}"} if author_id else None,
            "assignee": {"href": f"/api/v3/users/{assignee_id}"} if assignee_id else None,
        },
        "description": {"raw": description}
    }
    payload["_links"] = {k: v for k, v in payload["_links"].items() if v is not None}
    payload = {k: v for k, v in payload.items() if v is not None}
    return payload 