  Discovery Phase:

   1. How should the system handle a JSON file with a list of URLs? Should it process all of them in one go, or should the user select which ones to process?.
   *The system collets all the Json data, creates a queue of task to be processed whenerev possibile. Json data may be simple like { 'radioUrl': data}*
   
   2. When a name is derived from a URL, what is the desired format? For example, if the URL is http://example.com/station.mp3, should the name be station,
      example.com, or something else?
      *Name has to be extracted from title or domain of the url*
      
   3. What is the expected behavior when a playlist (.m3u, .pls) contains multiple valid streams? Should it propose all of them, or just the first one as currently
      specified?
      *There is a defualt to choose, to be defined selecting the one with best popularity*

   4. The spec mentions a timeout for scraping a URL. What should the default timeout be?
      *Let it be 30 secs for now*

   5. How should the system handle redirects (e.g., HTTP 301/302)? Should it follow them?
   *yes*

  Validation and Addition Phase:

   1. How should the system present the proposals to the user in the text-based interface? A numbered list?
   *A numbered list like the one of gemini uses, I waneed an interface similar to that*

   2. *What commands should be available to the user in the interactive validation phase? <list> represents list of proposals, <id> to show/edit a detail, <ok>, or <cancel> in detail to save or not a radio source, and returning to list, <reject> in detail to remove a proposal from list, a command to define to close and return to "main*

   3. How should the user provide the image/logo for the radio source? Should they provide a URL to the image, or upload a file? *yes an upload of a local image or remote via url*

   4. What happens if the user tries to add a streamUrl that already exists in the database? Should it be rejected, or should the existing entry be updated? *yes system puts a message and reject proposal*

   5. For the country field, should there be a predefined list of countries, or can the user enter any text? *yes a predefined country from an Internet standard*

to continue next session: ask Gemini to "continue with the implementation of the radio source discovery and validation feature". I will then check the current branch and the latest commit to understand the context and proceed from where we left of


Aspetto	Suggerimento
User Story	Aggiungi un persona o ruolo più preciso: es. “As a CLI user…” o “As a content curator…”
Acceptance Criteria	Evita ambiguità: es. “adds, if needed, other infos” → specifica quali sono obbligatorie e quali opzionali
Edge Cases	Ottimo che ci siano! Puoi espanderli con expected behavior (es. “If duplicate streamUrl is found, system rejects with error XYZ”)
FR-008	La frase “No validation will be provided…” è un po’ ambigua. Intendi che il sistema accetta anche dati parziali? Specifica meglio.
Entity fields	Hai un piccolo typo: ¯ image_description → probabilmente volevi imageDescription o imageUrl
Testabilità	
Puoi aggiungere esempi di input/output per ogni scenario, così Copilot può generare test unitari o CLI stub più facilmente


