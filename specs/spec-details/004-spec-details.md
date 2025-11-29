# Question 1: Stream Analysis Strategy - Which approach should be prioritized?
Context: Your "Informazioni per il task.md" mentions three options for analyzing streams without explicit extensions (curl headers, ffmpeg, content-type). The spec needs to define the analysis strategy.

What we need to know: What is the priority order and fallback strategy for stream analysis?

Suggested Answers:

Option	Answer	Implications
A	Headers-first (lightweight): Try curl -I for content-type → if fails, use ffmpeg -i	Fastest, minimal resource usage, but some streams don't expose proper headers
B	FFmpeg-first (reliable): Use ffmpeg -i as primary method → fall back to headers only if ffmpeg fails	Most reliable detection, works with all formats, but slower and requires ffmpeg installed
C	Dual-validation (robust): Always check both headers AND ffmpeg, compare results, use ffmpeg as authoritative source	Most accurate, catches mismatched headers, but doubles analysis time (~60s → ~120s, may violate SC-001)
Custom	Provide your own answer	Specify your preferred analysis strategy
Your choice: `C`

# Question 2: StreamType Entity - How detailed should classification be?
Context: You propose a new StreamType entity with protocol, format, metadata. The spec should clarify the scope of this entity.

What we need to know: Should StreamType be a simple enum/lookup table or a full entity with relationships?

Suggested Answers:

Option	Answer	Implications
A	Simple classification table: StreamType is a lookup table with predefined combinations (e.g., "HTTP-MP3-Icecast", "HLS-AAC-None"). Fixed ~10-15 known types	Easy to implement, fast classification, but rigid - can't handle new stream type combinations
B	Component-based: Separate tables for Protocol, Format, Metadata - StreamType links them together. Each stream gets 3 foreign keys	Flexible, can represent any combination, but more complex queries and relationships
C	Hybrid approach: StreamType stores common combinations (80% of cases) + a "custom" type with JSON field for unusual streams	Balances simplicity with flexibility, good query performance for common cases
Custom	Provide your own answer	Specify how StreamType should be structured
Your choice: `A`

# Question 3: Non-secure Streams (FR-004) - What's the security policy?
Context: FR-004 mentions rejecting "non-secure" streams (HTTP vs HTTPS?) but this needs clarification.

What we need to know: Should HTTP streams be rejected, warned about, or accepted?

Suggested Answers:

Option	Answer	Implications
A	Reject all HTTP: Only HTTPS streams are accepted, HTTP streams return validation error	Most secure, but eliminates ~70% of existing radio streams (many still use HTTP)
B	Accept with warning flag: HTTP streams are classified as valid but flagged as "insecure" in metadata, user sees warning in stage 002	Balances security with practicality, user makes final decision
C	Accept all protocols: No security filtering at stage 003, leave security decisions to user at stage 002	Maximum compatibility, but no automated security checks
Custom	Provide your own answer	Specify the security policy
Your choice: `B`

# Question 4: RTMP/RTSP Support - In scope or future enhancement?
Context: Your documentation mentions RTMP/RTSP protocols, but these require different tools (not just curl/ffmpeg over HTTP).

What we need to know: Should RTMP/RTSP be supported in this first implementation?

Suggested Answers:

Option	Answer	Implications
A	HTTP/HTTPS only (v1): Support only HTTP-based streams (Direct, HLS, Icecast/Shoutcast). RTMP/RTSP explicitly rejected with clear error message	Simpler implementation, covers ~90% of radio streams, clear scope for v1
B	Basic RTMP/RTSP detection: Detect rtmp:// and rtsp:// URLs, classify them, but validation may be limited	Broader protocol support, but requires additional tooling (rtmpdump, vlc, etc.)
C	Full multi-protocol support: Support HTTP, RTMP, RTSP with complete validation for all	Most comprehensive but significantly increases complexity and dependencies
Custom	Provide your own answer	Specify protocol scope
Your choice: `A`

# Question 5: Playlist Handling - Which stage processes playlists?
Context: Spec 001 mentions parsing playlists (.m3u, .pls), but spec 003 doesn't clarify if playlist analysis happens here or in stage 001.

What we need to know: Does stage 003 (analyze-and-classify) handle playlist parsing, or does it only validate the final stream URL passed from stage 001?

Suggested Answers:

Option	Answer	Implications
A	003 receives only direct stream URLs: Stage 001 parses playlists and extracts stream URLs → Stage 003 only validates direct audio streams	Clear separation of concerns, 003 is simpler, but 001 needs playlist parsing logic
B	003 handles everything: Stage 003 detects and parses playlists, extracts stream URLs, validates them, then passes back to 001	Centralized stream validation logic, but 003 becomes more complex
C	Hybrid: 003 detects if URL is a playlist and returns "PLAYLIST" classification → 001 re-parses and extracts URLs → 003 validates extracted URLs	Most flexible but requires multiple passes
Custom	Provide your own answer	Specify where playlist parsing belongs
Your choice: `B`

Please respond with your choices using this format:

Q1: `C` (note: I want to analyze consequences, I am very aware of the the problem of using a product installed as ffmpeg not web based services. Perhaps must add to constitution that the application requires ffmpeg installed and functional. We can limit to Linux/Unix if required.)
Q2: `A`
Q3: `B` (note: important so signal to the user if http)
Q4: `A`
Q5: `B` (note: I prefer to centralize also playlist analysys, to be added section for playlist, may be posponed not in this iteration. If needed propose alter the specs 001 and 002 to take in account this choice)

Commit of today: 20.10.2025
* Centralized stream analysis in spec 003 (using curl + ffmpeg)
* Predefined StreamType lookup table (14 types)
* HTTP security warnings (isSecure flag)
* Protocol scope (HTTP/HTTPS only, no RTMP/RTSP in v1)
* Playlist detection (parsing deferred to v2)
* ffmpeg dependency documented for Linux/Unix

detail:
Spec 003 (Analyze and Classify Stream) - Updated:
✅ Dual validation strategy (Q1-C): Both curl + ffmpeg, with ffmpeg as authoritative
✅ StreamType as lookup table (Q2-A): 14 predefined stream types including special "PLAYLIST" type
✅ HTTP streams accepted with warning (Q3-B): isSecure: false flag for HTTP streams
✅ HTTP/HTTPS only (Q4-A): RTMP/RTSP explicitly rejected
✅ Centralized playlist handling (Q5-B): Playlists detected but parsing deferred to v2
✅ System prerequisites section: ffmpeg requirement documented, Linux/Unix environment

Spec 001 (Discover Radio Source) - Updated:
✅ Delegates all validation/classification to spec 003
✅ Handles spec 003 responses (isValid, streamTypeId, isSecure)
✅ Playlist detection: notifies user "not supported in v1"
✅ Passes security flags to spec 002
✅ Updated entity to include streamTypeId and isSecure fields

Spec 002 (Validate and Add Radio Source) - Updated:
✅ Receives pre-validated proposals from spec 001 (via spec 003)
✅ Displays security warning for HTTP streams (isSecure: false)
✅ Makes streamTypeId and isSecure READ-ONLY (set by spec 003)
✅ Adds duplicate streamUrl validation
✅ Clear separation of user-editable vs system-set fields

Note on ffmpeg dependency: This architectural decision centralizes stream analysis in spec 003, making it a critical dependency. The system will check for ffmpeg at startup and fail gracefully if missing.

Playlist support: Deferred to future iteration (v2) - spec 003 will detect and classify as "PLAYLIST" type, but no parsing/extraction happens in v1.