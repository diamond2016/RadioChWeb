# Proposal Detail Edit Feature

Summary
-------
This change implements an editable Proposal detail page and supporting service layer.

What I changed
---------------
- Added `service/proposal_service.py` with `update_proposal` to update user-editable fields.
- Converted `templates/proposal_detail.html` into an edit form (POST) for fields: `name`, `website_url`, `country`, `description`, `image` (mapped to `image_url`).
- Implemented POST handling in `route/proposal_route.py` to call the new `ProposalService` and redirect to the proposals list.
- Added CSRF protection hooks and included `csrf_token()` in forms; CSRF is disabled in tests (`tests/conftest.py`).
- Added `tests/unit/test_proposal_update.py` which exercises the edit POST and verifies DB updates.
- Added flash message rendering to `templates/proposals.html` so update/approve feedback is visible.

Testing
-------
- All unit tests pass locally: `50 passed`.
- The project test run includes coverage for the new service and route.

Notes & Next Steps
------------------
- Integration test for edit → approve flow is still pending.
- Optionally add server-side validation (`ProposalValidationService`) for edits before saving.
- Consider enabling full CSRF in tests by creating and sending tokens if you prefer stricter tests.

Files of interest
-----------------
- `service/proposal_service.py`
- `route/proposal_route.py`
- `templates/proposal_detail.html`
- `templates/proposals.html`
- `tests/unit/test_proposal_update.py`

Please review the changes and the tests; I can open a PR now with these commits for you to review.
