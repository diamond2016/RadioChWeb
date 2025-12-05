# Smoke test for auth pages using Flask test client
import sys
from pathlib import Path

# Ensure project root is on path so `import app` works when running the script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app

def fetch(path):
    with app.test_client() as c:
        r = c.get(path)
        print(f"GET {path} -> {r.status_code}, {len(r.data)} bytes")
        snippet = r.data.decode('utf-8', errors='replace')[:400]
        print('--- snippet ---')
        print(snippet)
        print('--- end ---\n')

if __name__ == '__main__':
    fetch('/auth/login')
    fetch('/auth/register')
