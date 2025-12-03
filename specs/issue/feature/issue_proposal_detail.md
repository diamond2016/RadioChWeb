## issue feature: "manage page proposal_detail.html which allows editing of a view and editing of a Proposal data


The page "proposal_detail.html" was updated. 

Its purpose is to present to the user all data of a Proposal entity, 

- action "Update Proposal" system collects data from the page and updates entity

- action "Return to Proposals" return to list of proposals (prev page, proposal.index). 

You have to check the fields if correct, and assign two different classes, 
one for fields not editable: stream_url, created_at
and another class for other fields (editable).

1. verify proposal_route if has correct routing to proposal_detail.html and correct routing for editing and returning to list of proposals.";
2. if necesary (there is the field description) apply secutrity or use a Flask Form WTF
3. verify proposal_service if has correct method to update a Proposal entity from data collected from the page proposal_detail.html
4. verify proposal_repository if has correct method to update a Proposal entity in the database.

## IMPLEMENTATION PLAN

1. Update proposal_detail.html: convert the display into an HTML <form method="post"> that submits to url_for('proposal.proposal_detail', id=proposal.id) and includes editable inputs for name, website_url, country, description, image_url; keep stream_url and created_at as read-only/disabled fields and fix typos (contry → country). `OK`

1. Edit proposal_route.py proposal_detail view: on POST, read request.form values, map them to the expected DTO or dict, call RadioSourceService.update_proposal(proposal_id, updates), flash success/failure, and redirect(url_for('proposal.index')). `OK`

1. Verify RadioSourceService.update_proposal signature in radio_source_service.py and adapt the route to either construct the required ProposalUpdateRequest DTO (from model.dto) or pass a simple mapping if the service accepts it. `I PREFER REFACTOR In proposal_service radio source servic is another domain If possible move the code to the new service layer proposal_service.py.` 

1. Add tests: tests/unit/test_proposal_update.py (or integration test) — create a Proposal fixture, POST new values to /proposal/<id> route using the test client, assert the DB row was changed via ProposalRepository.find_by_id, and confirm the response redirects to proposals list. `OK`

Small polish: add server-side validation via ProposalValidationService if required, and display flashed messages on proposals.html. `NOT NOW`

Further Considerations
Reuse vs new service: Option A — reuse RadioSourceService.update_proposal (recommended). 
Option B — add service/proposal_service.py if you want proposal-specific logic isolated. `YES OPTION B`

CSRF: If you plan to enable CSRF (Flask-WTF), add the token to the form and tests. 
For now tests can POST without CSRF. `YES`

Atomicity: If updates must be transactional with other operations, consider performing DB operations inside a transaction.
Please review this draft plan and tell me if you want me to proceed with these exact steps, prefer creating a dedicated proposal_service, or include CSRF and extra validation now. `NOT NOW`