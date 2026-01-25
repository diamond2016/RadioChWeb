import sys
from pathlib import Path

# Ensure the api/ directory is on sys.path so `import main` works from tests
API_DIR = Path(__file__).resolve().parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))