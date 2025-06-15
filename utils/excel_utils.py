import pandas as pd
from datetime import datetime

def read_users_from_excel(excel_file):
    """
    엑셀 파일에서 사용자 정보를 읽어 리스트로 반환
    컬럼: login, email, firstName, lastName, password, (선택)admin, (선택)status
    """
    df = pd.read_excel(excel_file)
    required_columns = ['login', 'email', 'firstName', 'lastName', 'password']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"필수 컬럼 누락: {missing_columns}")
    users = []
    for _, row in df.iterrows():
        user = {
            "login": row['login'],
            "email": row['email'],
            "firstName": row['firstName'],
            "lastName": row['lastName'],
            "password": row['password'],
            "admin": row.get('admin', False),
            "status": row.get('status', 'active')
        }
        users.append(user)
    return users

def read_work_packages_from_excel(excel_file):
    """
    엑셀 파일에서 work package 정보를 읽어 리스트로 반환
    컬럼: subject, project_id, type_id, status_id, priority_id, author_id, assignee_id, category_id, start_date, due_date, description
    """
    df = pd.read_excel(excel_file)
    required_columns = ['subject', 'project_id', 'author_id']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"필수 컬럼 누락: {missing_columns}")
    work_packages = []
    for _, row in df.iterrows():
        def format_date(val):
            if pd.isna(val):
                return None
            if isinstance(val, datetime):
                return val.strftime('%Y-%m-%d')
            if isinstance(val, str) and len(val) >= 10:
                return val[:10]
            return str(val)
        wp = {
            "subject": row['subject'],
            "project_id": int(row['project_id']),
            "type_id": int(row['type_id']) if 'type_id' in df.columns and not pd.isna(row.get('type_id')) else 1,
            "status_id": int(row['status_id']) if 'status_id' in df.columns and not pd.isna(row.get('status_id')) else 1,
            "priority_id": int(row['priority_id']) if 'priority_id' in df.columns and not pd.isna(row.get('priority_id')) else 9,
            "author_id": int(row['author_id']),
            "assignee_id": int(row['assignee_id']) if 'assignee_id' in df.columns and not pd.isna(row.get('assignee_id')) else None,
            "category_id": int(row['category_id']) if 'category_id' in df.columns and not pd.isna(row.get('category_id')) else None,
            "start_date": format_date(row['start_date']) if 'start_date' in df.columns else None,
            "due_date": format_date(row['due_date']) if 'due_date' in df.columns else None,
            "description": str(row['description']) if 'description' in df.columns and not pd.isna(row.get('description')) else ""
        }
        work_packages.append(wp)
    return work_packages 