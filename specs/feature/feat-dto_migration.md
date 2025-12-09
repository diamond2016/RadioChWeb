# DTO migration snapshot — unified plan (Option B, top-down)

## TL;DR
Migrate to canonical DTOs: ProposalDTO, RadioSourceDTO, StreamTypeDTO, UserDTO, and a single ValidationDTO. Use Pydantic v2 model_dump(exclude_none=True) for partial updates where None = no change. Fix mutable defaults in validation DTO. Implement service-level update logic, update routes to build DTOs from forms, update templates to read nested DTO fields, and ensure repositories eager-load relationships used by DTO conversion.

## Purpose
Provide a single, concise document that:

## Lists work to do top-down (per route + cross-cutting).
- Consolidates unique guidance found earlier.
- Includes concrete, minimal code snippets to apply the most urgent changes.

## Canonical DTOs to use
- ProposalDTO
- RadioSourceDTO
- StreamTypeDTO
- UserDTO
- ValidationDTO (consolidates previous ValidationRequest/ValidationResult)

## Overall strategy (short)
Services accept/return DTOs only; convert ORM ↔ DTO at service boundary with XDTO.model_validate(orm_obj) and XDTO.model_validate(updated_orm) for returns.
Routes convert form/JSON → DTO and call services.
Partial updates: accept full DTO but treat None as “no change”; use model_dump(exclude_none=True) to extract changes.
Templates consume DTOs (nested objects) and must guard for None.
Repositories should eager-load relations (user, stream_type) used by DTOs to allow nested DTO creation via from_attributes=True.

## Per-route work (top-down)
## Analysis (route/analysis_route.py + service/stream_analysis_service.py)
Ensure analysis service returns a DTO (e.g., StreamAnalysisResult or included under ValidationDTO).
Route: call service, receive DTO(s), pass DTOs to templates (no ORMs).
Template: use DTO attributes, guard nested fields.

## Auth (route/auth_route.py + service/auth_service.py)
Keep Flask-Login user_loader returning ORM (Flask-Login expects model-like object).
Public auth methods (register_user, change_password) should return UserDTO via UserDTO.model_validate(orm).
Routes/templates should use UserDTO when not relying on current_user behavior.

## Database / Admin pages (route/database_route.py + repositories)
Add repository query variants that eager-load user and stream_type for lists shown in admin pages.
Routes return lists of DTOs via services.
Templates updated to DTO fields and safe datetime formatting.

## Listen (route/listen_route.py + templates/listen_player.html)
RadioSourceService.get_radio_source_by_id() returns RadioSourceDTO.
Route passes DTO to template / JS; template uses source.stream_url, source.stream_type.display_name (guarded).

## Main (route/main_route.py + templates/index.html)
Replace direct repo calls with service calls returning DTO lists for homepage.
Template iterates DTOs and formats created_at only if present.

## Proposal (route/proposal_route.py + proposal_service.py + repository)
Implement:
- get_proposal(id) -> ProposalDTO | None
- get_all_proposals() -> list[ProposalDTO]
- create_proposal(data) -> ProposalDTO
- update_proposal(id, updates: ProposalDTO) -> ProposalDTO | None (Option B)

## Route update handler:
Fetch current DTO (for identity/read-only values).
Build update DTO where optional fields are None when form omitted.
Call service update_proposal.
Template: use proposal.user.id / proposal.user.email, proposal.stream_type.display_name, guarded created_at.

## Radio Source (route/radio_source_route.py + service/radio_source_service.py)
Services return RadioSourceDTO.
save_from_proposal() returns RadioSourceDTO.
Routes construct RadioSourceDTO from forms for updates.
Templates use DTO fields and guard for nested DTOs.

## Cross-cutting tasks
Repositories: add selectinload/joinedload where DTO nested fields required.
Timestamps: standardize DTO created_at/updated_at as datetime | None if possible; otherwise use ISO strings and document format.
Read-only fields: document and protect (e.g., id, stream_url, stream_type_id, is_secure).

## Tests: update unit tests to build/expect DTOs not ORMs.
Backwards compatibility: create small adapter helpers in services to accept ORM or DTO during migration.
Concrete patches / code snippets (apply these first)
Replace mutable-default validation DTO with ValidationDTO.

```python
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class SecurityStatusDTO(BaseModel):
    is_secure: bool
    warning_message: Optional[str] = None

class ValidationDTO(BaseModel):
    is_valid: bool = True
    message: str = ""
    security_status: Optional[SecurityStatusDTO] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)

Notes:

Prevents shared mutable lists (errors, warnings).
Use ConfigDict(from_attributes=True) to allow model_validate from ORM attributes.

Implement ProposalService.update_proposal (Option B: None = no change).


```python
# ...existing code...def update_proposal(self, proposal_id: int, updates: ProposalDTO) -> ProposalDTO | None:    proposal_orm = self.proposal_repo.find_by_id(proposal_id)    if proposal_orm is None:        return None    # Pydantic v2: extract only provided fields (exclude None)    changes = updates.model_dump(exclude_none=True)    # Protect identity/read-only fields    for readonly in ("id", "stream_url", "stream_type_id", "is_secure"):        changes.pop(readonly, None)    # No-op guard    if not changes:        return ProposalDTO.model_validate(proposal_orm)    # Apply changes to ORM    for key, value in changes.items():        setattr(proposal_orm, key, value)    # Persist and return updated DTO (repo.update should commit/refresh)    updated = self.proposal_repo.update(proposal_orm)    return ProposalDTO.model_validate(updated)# ...existing code...
```
Notes:
Handles partial updates where None = no change.
or None maps empty form values to None (no change). Remove or None if empty string should clear value.
Template guidance (examples)
Guard nested fields:

```html
<!-- Use DTO fields and guard for None --
><h1>{{ proposal.name }}</h1><p>By: {{ proposal.user.email if proposal.user else 'Unknown' }}</p><p>Type: {{ proposal.stream_type.display_name if proposal.stream_type else 'Unknown' }}</p><p>Created: {{ proposal.created_at.strftime('%Y-%m-%d %H:%M') if proposal.created_at else 'Unknown' }}</p>
```

Checklist (apply & verify)
 Replace validation DTO (validation.py) with ValidationDTO (use Field(default_factory=list)).
 Implement update_proposal in proposal_service.py per snippet.
 Update proposal_route.py update POST to construct DTO and call service.
 Update templates to use DTO nested fields and safe datetime formatting.
 Add eager-loading (selectinload) in ProposalRepository for user and stream_type.
 Update other routes to stop returning ORMs to templates — return DTOs instead.
 Update tests to construct/expect DTOs; run pytest -q.
 Document read-only fields and None semantics (None = no change).


Include test changes in PR and record local environment (Python version, OS) used to validate.