1. JSON Input Format
You mentioned: "Json data may be simple like { 'radioUrl': data}"

Can you provide a complete example? Should it support multiple formats like:


// Format A: Simple array{  "urls": [    "http://stream1.example.com",    "http://stream2.example.com"  ]}// Format B: Objects with metadata[  {    "radioUrl": "http://stream1.example.com",    "name": "Station 1",    "country": "IT"  },  {    "radioUrl": "http://stream2.example.com"  }]// Format C: Single URL object{  "radioUrl": "http://stream.example.com"}
Should all these formats be supported?
*All formats are allowed*

2. Task Queue Processing
You said: "creates a queue of task to be processed whenever possible"

Should processing be sequential (one at a time) or parallel (multiple concurrent connections)?
Should the user see progress in real-time, or just get all results at the end?
*sequential with info on progress*

If one URL fails, should it continue with the rest?
3. "Best Popularity" in Playlists
You mentioned: "selecting the one with best popularity"

How is popularity determined? Is there metadata in the playlist, or do you need to query an external API (like Radio Browser API)?
If no popularity data is available, should it default to the first stream, or skip the playlist?
*this is first stream*

4. Interface Similar to Gemini
You want: "an interface similar to that typical code assit like Copilot, Gemini, Claude when run from CLI, with:
* Numbered list with descriptions
* Ability to scroll through proposals
* Inline editing of fields

*Adapt the proposals to lists of tasks and details with wizxard to collect data*

Proposals Found (3):[1] Stream: http://example.com/stream.mp3    Name: Example Radio    Country: [Not set]    Website: http://example.com    Status: ⚠️ Incomplete[2] Stream: http://another.com/live    Name: Another Station    Country: US    Website: http://another.com    Status: ✓ ReadyCommands: <list> <id> <ok> <cancel> <reject> <quit>Enter command:
5. Detail View Commands
You mentioned commands in detail view: <ok>, <cancel>, <reject>

When showing a detail, should it look like:


=== Proposal #1 Details ===1. streamUrl: http://example.com/stream.mp32. name: Example Radio3. country: [Not set]4. websiteUrl: http://example.com5. description: [Not set]6. imageUrl: [Not set]Commands:  <edit 1-6> - Edit a field  <ok>       - Save and return to list  <cancel>   - Discard changes and return  <reject>   - Remove from proposalsEnter command:
6. Image Upload Implementation
For local image upload in a CLI context:

Should the user provide a file path (e.g., /home/user/logo.png)?
Should the system copy it to a project folder (e.g., assets/images/)?
Should it validate image format (PNG, JPG only)?
7. Country Standard - Which One?
You said: "a predefined country from an Internet standard"
Which standard?
*ISO 3166-1 alpha-2: IT, US, GB (2 letters)*

ISO 3166-1 alpha-3: ITA, USA, GBR (3 letters)
Full names: Italy, United States, United Kingdom

8. Main Menu Return Command
You mentioned: "a command to define to close and return to main"
What should this command be? Options:

<quit> or <exit> - Exit the validation phase entirely
*<done> - Finish validation and add all marked proposals to database*
<main> - Return to main menu without saving
Please clarify these points so I can implement exactly what you nee