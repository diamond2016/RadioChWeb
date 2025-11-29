## Summary of organization of web  interface

## Templates

- index.html: home page of website. Displays an initial section of welcome and data in rows, three columns by row, consisting in radio sources, ready to be selected for playing. 
Every radio source card, displays (to be organized layout):
- name
- streamType description
- country
- description
- image
- link to stream (streamUrl)

- stream.html: modal page which presents the same data of the radio source card of index.html, and streama the dario url.

- proposal.html: page where user make the step of discovering and analyzing a possibile stream url. Consists in a first section where user may input a link (for possibile stream url) or upload a file (of possible stream urls to anayze). Button ton start analyze.
Under the input section a list of url analyzed and result of analysis. 
URL         ANALYSYS                DATA (if ok)

....        x.....x..                streamUrl isSecure data from anaysys

...         error message             -

button to Delete some proposal, Cancel to come back

- radio_source.html: page where user make the step of consulting proposals saved in db, and saving a proposal as a new radio source (completing data) 
Consists in a list of proposals and clicking row, under the list there is a section where user may read and complete a proposal, and save in db as radio_source if wanted.
The radio source data displays (to be organized layout):

    streamUrl
    name (to be given)
    websiteUrl
    streamType description
    isSecure
    country
    description (to be given)
    image_url (to be given)

buttom Save, Delete, Cancel

database.html
page of management, displays list of: stream types, proposals, radio_sources: as in db, a tabbed page in three subsection. Clicking on menu displays the data. 
- stream types: only consulting data
- proposals: consult and possible delete entity (row)
- radio_sources: consult and possible delete entity (row) 


## Routes

- main_bp:
index() /
stream(url) /stream 

- radio_source_bp:
proposal_index() /proposal
proposal_analyze() /proposal_analyze
proposal_create() /proposal_create
proposal_delete() /proposal_delete

logic to come back to proposal_index and index

- radio_source_bp():
radio_source_index() /radio_source
radio_source_create() /radio_source_create

- database_bp():
database_index() /database
database_stream_type_index() /database
database_proposal_index() /database_proposal
database_radio_source_index() /database_radio_source
database_proposal_delete() /database_proposal_delete
database_radio_source_delete() /database_radio_source_delete

