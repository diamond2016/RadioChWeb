# scripts/create_admin.py
import sys
from pathlib import Path
import argparse
# Ensure project root is on path so `import app` works when running the script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model.dto.user import UserDTO



def main():
    from service.auth_service import AuthService
    from app import app
    with app.app_context():
        p = argparse.ArgumentParser()
        p.add_argument('--email', required=True)
        p.add_argument('--password', required=True)
        args = p.parse_args()
        user_dto: UserDTO = UserDTO(
            id=0,  # id will be set by the database
            email=args.email,
            role='admin'
        )
        AuthService(app).register_user(user=user_dto, password=args.password)
        print(f"Admin user '{args.email}' created.")

if __name__ == '__main__':
    main()