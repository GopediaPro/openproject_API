from dotenv import load_dotenv
import os
import pandas as pd
import requests
import json
from requests.auth import HTTPBasicAuth
import sys
from urllib.parse import urljoin

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenProject 설정
OPENPROJECT_URL = os.getenv("OPENPROJECT_URL")  # 실제 OpenProject URL로 변경
API_KEY = os.getenv("API_KEY")  # 실제 API 키로 변경
ADMIN_USER = os.getenv("ADMIN_USER")  # 관리자 사용자명

class OpenProjectUserCreator:
    def __init__(self, base_url, api_key, admin_user):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.admin_user = admin_user
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(admin_user, api_key)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def create_user(self, username, email, first_name, last_name, password):
        """단일 사용자 생성"""
        url = urljoin(self.base_url, '/api/v3/users')
        print("url check", url)
        user_data = {
            "login": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "password": password,
            "status": "active"
        }
        
        try:
            response = self.session.post(url, json=user_data)
            
            if response.status_code == 201:
                print(f"✅ 사용자 생성 성공: {username} ({email})")
                return True, response.json()
            else:
                print(f"❌ 사용자 생성 실패: {username} - {response.status_code}: {response.text}")
                return False, response.text
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류: {username} - {str(e)}")
            return False, str(e)

    def bulk_create_users(self, excel_file):
        """Excel 파일에서 사용자 정보를 읽어 일괄 생성"""
        try:
            # Excel 파일 읽기
            df = pd.read_excel(excel_file)
            print("df", df)
            # 필수 컬럼 확인
            required_columns = ['username', 'email', 'first_name', 'last_name', 'password']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ 필수 컬럼이 누락되었습니다: {missing_columns}")
                return False
            
            print(f"📋 총 {len(df)} 명의 사용자를 생성합니다...\n")
            
            success_count = 0
            failure_count = 0
            
            # 각 행별로 사용자 생성
            for index, row in df.iterrows():
                username = str(row['username']).strip()
                email = str(row['email']).strip()
                first_name = str(row['first_name']).strip()
                last_name = str(row['last_name']).strip()
                password = str(row['password']).strip()
                
                # 빈 값 체크
                if not all([username, email, first_name, last_name, password]):
                    print(f"⚠️  행 {index + 2}: 빈 값이 있어 건너뜁니다")
                    failure_count += 1
                    continue
                
                success, _ = self.create_user(username, email, first_name, last_name, password)
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
            
            print(f"\n📊 결과:")
            print(f"   성공: {success_count}명")
            print(f"   실패: {failure_count}명")
            print(f"   총합: {success_count + failure_count}명")
            
            return True
            
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {excel_file}")
            return False
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            return False

def main():
    # 설정 확인
    if OPENPROJECT_URL == "https://sd.lyckabc.xyz":
        print("❌ OPENPROJECT_URL을 실제 OpenProject 도메인으로 변경해주세요")
        sys.exit(1)
    
    if API_KEY == "your-api-key-here":
        print("❌ API_KEY를 실제 API 키로 변경해주세요")
        sys.exit(1)
    
    # Excel 파일 확인
    excel_file = "./users.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Excel 파일을 찾을 수 없습니다: {excel_file}")
        sys.exit(1)
    
    # 사용자 생성 실행
    creator = OpenProjectUserCreator(OPENPROJECT_URL, API_KEY, ADMIN_USER)
    creator.bulk_create_users(excel_file)

if __name__ == "__main__":
    main()