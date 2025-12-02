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