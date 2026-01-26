import sys
from pathlib import Path

# Ensure the api/ directory is on sys.path so `import main` works from tests
API_DIR = Path(__file__).resolve().parent
# Add repository root (parent of api/) so `import api...` works from tests run
PARENT_DIR = API_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))