### Architecture & Data Flow
Where are proposals stored? Should they be in-memory only during the session, or persisted to a temporary database table/file before user validation?
*The proposals are store in database in an entity to "consume" in the 2^ stage of discovery (that is validate and add)*

### State management: After running discover, how does the validate-and-add phase access the proposals? Same CLI session, or can the user close and resume later?
*The proposals not consumed or not rejected (deleted) explicity by user, will be always available in a list, presented to the user in a CLI text based (interface similar to what agents CLI do).*

### Main 
*at the moment the `main` of application is not properly defined due to the early stage of development. I will be described, to allow a first architecture we can prepare a simple menu with "head radio source" "search database of radios", "import or add a new source". The third will enter the discover and add stages*

### Batch processing: When processing a JSON file with multiple URLs, should failures (unreachable URLs, invalid formats) stop the entire batch or just skip and continue?
*Stop the execution providing clear explanmation to the user*

### Data Validation & Quality*
Minimum required fields: You mention "minimum of valid url, name, website" - does this mean:
streamUrl (required)
name (required)
websiteUrl (required)
All other fields (country, description, image) are optional?
*yes*

### Stream validation: Should the system actually attempt to connect to the stream URL and verify it's playable, or just check the URL format and content-type header?
*I want to explore the second option (granted the first validation), with a small app like "proof of content"*

### Country selection: Which Internet standard for countries? ISO 3166-1 alpha-2 (US, IT), alpha-3 (USA, ITA), or full names (United States, Italy)?
*ok ISo codes*

### Playlist Handling
"Best popularity" selection: How does the system determine popularity from a playlist? Is there metadata in .m3u/.pls files, or do you need to query an external API?
*not of use by now, idea to refine*

### Multiple streams from playlist: If a playlist has 10 streams, should they all become separate proposals, or should the system pick only one?
*System picks one stream for radio source, if multiple of the same radio source picks the first ok*

### Image/Logo Management
Image storage: Should images be stored as:
File paths (uploaded to a local directory)? *this option*
URLs (referenced remotely)?
Base64 encoded in the database?
Both local and remote options?
Image field naming: Spec 001 mentions image, spec 002 mentions image_description - which is correct? Should it be imageUrl or imagePath?

### CLI Interface Details
Command syntax: For the validation phase, you mentioned commands like <list>, <id>, <ok>. Should the actual syntax be:
Just numbers/words: list, 1, ok, cancel? 
*numbers and description, click on line highlihted when curso goes on to select
All commands also in "detail" may be managed by menu 1..2..*

### Edit interface: When editing a proposal (showing details), should all fields be editable line-by-line, or should there be specific commands like set name "New Name", set country IT, etc.?
*We can apply line by line in wizard.*

### Error Handling & Edge Cases
Duplicate detection: Should the system check for duplicates by exact streamUrl match only, or also consider similar names/websites?
*for now simple check of url*

### Failed discoveries: Should failed URL attempts be logged somewhere for review, or just displayed and forgotten?
*logging in a file for internal review, not for user but for developer*

### Partial data: Can a user save a proposal with only the 3 minimum fields, or should the system encourage/require more complete data?
*yes, partial data is allowed, priority on speed with respect to completeness* 

### Need of editing data
Other spec will cover functionality to edit data od an existing radio (with resuability of most of 002 spec)