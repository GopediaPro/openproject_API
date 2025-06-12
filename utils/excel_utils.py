import pandas as pd

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