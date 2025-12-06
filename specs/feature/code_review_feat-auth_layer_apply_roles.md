# Code review – feat/auth layer apply roles

## Overview

- PR Phase 2 autenticazione: introdotti ruoli (user vs admin) e tracciamento dei creator per proposte e analisi. [file:1]
- Applicato Black a molti file (service, route, test, app.py). [file:1]
- Aggiornati i test per usare nuovi fixture di autenticazione e pattern con transazioni annidate. [file:1]

---
## Issues Identified

* In tests/unit/test_radio_source_service.py:

> @@ -158,11 +155,7 @@ def test_reject_proposal_success(
         assert result
         mock_proposal_repo.delete.assert_called_once_with(1)
 
-    def test_reject_proposal_not_found(
-        self,
-        radio_source_service,
-        mock_proposal_repo
-    ):
+    def test_reject_proposal_not_found(self, radio_source_service, mock_proposal_repo):
This assignment to 'test_reject_proposal_not_found' is unnecessary as it is [1]redefined before this value is used.
`OK SOLVED by removing the previous definition`.

* In tests/conftest.py:

>  from database import db
 from model.entity.stream_type import StreamType
+from model.entity.stream_analysis import StreamAnalysis
Import of 'StreamAnalysis' is not used.
`OK removed`

* In tests/conftest.py:

>  from database import db
 from model.entity.stream_type import StreamType
+from model.entity.stream_analysis import StreamAnalysis
+from model.entity.user import User
Import of 'User' is not used.

* In tests/conftest.py:

>  from database import db
 from model.entity.stream_type import StreamType
+from model.entity.stream_analysis import StreamAnalysis
+from model.entity.user import User
+from model.entity.radio_source import RadioSource
Import of 'RadioSource' is not used.

* In tests/conftest.py:

>  from database import db
 from model.entity.stream_type import StreamType
+from model.entity.stream_analysis import StreamAnalysis
+from model.entity.user import User
+from model.entity.radio_source import RadioSource
+from model.entity.proposal import Proposal
Import of 'Proposal' is not used.
`OK removed 3 entities non used`

* In specs/feature/feat-auth-layer-apply-roles.md:

> +1. Seed CLI (new) `scripts/create_admin.py` — minimal safe script:
+   ```python
+   # scripts/create_admin.py
+   import argparse
+   from app import app
+   from service.auth_service import AuthService
+
+   def main():
+       p = argparse.ArgumentParser()
+       p.add_argument('--email', required=True)
+       p.add_argument('--password', required=True)
+       args = p.parse_args()
+
+       AuthService(app).register_user(email=args.email, password=args.password, role='admin')
+       print(f"Admin user '{args.email}' created.")
+
+   if __name__ == '__main__':
+       main()
+   ```
+   

* Run locally (do not commit secrets): `python scripts/create_admin.py --email admin@example.com --password 'Strong!'`
The example scripts/create_admin.py in this spec passes the admin password via a --password command-line argument (lines 75–93 and the example invocation on line 94). Command-line arguments are visible in process listings and can be stored in shell history or other monitoring logs, which can expose the admin password to other local users or tooling.

Instead of accepting the password via CLI args, use a secure input method such as getpass.getpass() or read it from a protected environment variable or prompt inside the script, and update the usage example to avoid putting the password directly on the command line.