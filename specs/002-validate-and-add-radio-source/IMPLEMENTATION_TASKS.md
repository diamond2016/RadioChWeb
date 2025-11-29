# Implementation Tasks: Spec 002 - Validate and Add Radio Source

**Feature**: Validate and Add Radio Source
**Status**: Ready for Implementation
**Estimated Duration**: 2-3 days
**Priority**: P1 (blocks full workflow completion)

---

## 📋 Task Breakdown

### **Phase 1: Service Layer Implementation** (4-6 hours)

#### Task 1.1: Create Proposal Validation Service
**File**: `src/services/proposal_validation_service.py`

**Requirements**:
- ✅ Implement `ProposalValidationService` class
- ✅ Method: `validate_proposal(proposal_id: int) -> ValidationResult`
  - Check required fields: `streamUrl`, `name`, `websiteUrl` (non-null)
  - Validate URL formats
  - Return validation errors if any
- ✅ Method: `check_duplicate_stream_url(stream_url: str) -> bool`
  - Query RadioSourceRepository to check if stream URL already exists
  - Return True if duplicate found
- ✅ Method: `get_security_status(proposal_id: int) -> SecurityStatus`
  - Check `isSecure` flag from proposal
  - Return security status with warning message if HTTP

**Dependencies**: 
- ProposalRepository (existing)
- RadioSourceRepository (existing)

**Test Coverage**: 
- Unit tests for validation logic
- Duplicate detection tests
- Security status tests

---

#### Task 1.2: Create Radio Source Service
**File**: `src/services/radio_source_service.py`

**Requirements**:
- ✅ Implement `RadioSourceService` class
- ✅ Method: `save_from_proposal(proposal_id: int) -> RadioSourceNode`
  - Retrieve proposal from database
  - Validate proposal (call ProposalValidationService)
  - Check for duplicates
  - Create RadioSourceNode from proposal data
  - Set `createdAt` timestamp
  - Persist to database via RadioSourceRepository
  - Delete proposal after successful save
  - Return saved RadioSourceNode
- ✅ Method: `reject_proposal(proposal_id: int) -> bool`
  - Delete proposal from database
  - Return success status
- ✅ Method: `update_proposal(proposal_id: int, updates: dict) -> Proposal`
  - Update user-editable fields only: `name`, `websiteUrl`, `country`, `description`, `image`
  - Validate that `streamTypeId` and `isSecure` are not modified
  - Return updated proposal

**Dependencies**: 
- ProposalRepository
- RadioSourceRepository
- ProposalValidationService

**Test Coverage**: 
- Save proposal tests (success case)
- Duplicate rejection tests
- Validation failure tests
- Update proposal tests
- Read-only field protection tests

---

### **Phase 2: DTO Implementation** (1-2 hours)

#### Task 2.1: Create Validation DTOs
**File**: `src/dtos/validation.py`

**Requirements**:
- ✅ `ValidationResult` dataclass:
  - `is_valid: bool`
  - `errors: List[str]`
  - `warnings: List[str]`
- ✅ `SecurityStatus` dataclass:
  - `is_secure: bool`
  - `warning_message: Optional[str]`
- ✅ `ProposalUpdateRequest` dataclass:
  - `name: Optional[str]`
  - `website_url: Optional[str]`
  - `country: Optional[str]`
  - `description: Optional[str]`
  - `image: Optional[str]`

**Test Coverage**: 
- DTO validation tests
- Serialization tests

---

### **Phase 3: Textual TUI Integration** (4-6 hours)

#### Task 3.1: Create Proposal List View
**File**: `radioch_app.py` (update existing)

**Requirements**:
- ✅ Add DataTable widget to "Validate & Add" tab
- ✅ Display all proposals with columns: ID, Name, Stream URL, Type, Security Status
- ✅ Add refresh button to reload proposals
- ✅ Add selection handling (click to view details)
- ✅ Show "No proposals" message when list is empty
- ✅ Add security warning icon (⚠️) for HTTP streams

**UI Components**:
- DataTable or ListView for proposal list
- Refresh button
- Status indicators
- Empty state message

---

#### Task 3.2: Create Proposal Detail/Edit Screen
**File**: `radioch_app.py` or separate widget

**Requirements**:
- ✅ Display all proposal fields in a form
- ✅ Read-only fields: Stream URL, Stream Type, Security Status
- ✅ Editable fields: Name, Website URL, Country, Description, Image
- ✅ Input validation on edit
- ✅ Security warning display for HTTP streams
- ✅ Save button (enabled only when valid)
- ✅ Reject button
- ✅ Cancel button (return to list)

**UI Components**:
- Input fields (with labels)
- Static text for read-only fields
- Warning banner for HTTP streams
- Action buttons (Save, Reject, Cancel)

---

#### Task 3.3: Implement Save/Reject Actions
**File**: `radioch_app.py`

**Requirements**:
- ✅ Save action:
  - Validate proposal via service
  - Show validation errors in UI
  - Check for duplicates
  - Show duplicate error dialog
  - Show security confirmation for HTTP streams
  - Call `save_from_proposal` service method
  - Show success notification
  - Return to proposal list
  - Refresh list
- ✅ Reject action:
  - Show confirmation dialog
  - Call `reject_proposal` service method
  - Show success notification
  - Return to proposal list
  - Refresh list

**UI Components**:
- Confirmation dialogs
- Error/success notifications
- Loading indicators

---

### **Phase 4: Database Management Tab** (2-3 hours)

#### Task 4.1: Implement View Stream Types
**File**: `radioch_app.py`

**Requirements**:
- ✅ Query all stream types from database
- ✅ Display in DataTable: ID, Display Name, Protocol, Format, Metadata
- ✅ Add close/back button

---

#### Task 4.2: Implement View Radio Sources
**File**: `radioch_app.py`

**Requirements**:
- ✅ Query all radio sources from database
- ✅ Display in DataTable: ID, Name, Stream URL, Country, Security Status
- ✅ Add pagination (if needed)
- ✅ Add search/filter functionality
- ✅ Add close/back button

---

#### Task 4.3: Implement Run Migration
**File**: `radioch_app.py`

**Requirements**:
- ✅ Call `migrate.py` functionality
- ✅ Show migration progress
- ✅ Display migration results
- ✅ Show error messages if migration fails

---

### **Phase 5: Testing** (3-4 hours)

#### Task 5.1: Unit Tests
**File**: `tests/unit/test_proposal_validation_service.py`

**Test Cases**:
- ✅ Valid proposal passes validation
- ✅ Missing required fields fail validation
- ✅ Invalid URLs fail validation
- ✅ Duplicate stream URL detection
- ✅ Security status detection
- ✅ HTTP warning generation

**File**: `tests/unit/test_radio_source_service.py`

**Test Cases**:
- ✅ Save proposal creates RadioSourceNode
- ✅ Duplicate URL blocks save
- ✅ Validation errors block save
- ✅ Reject proposal deletes proposal
- ✅ Update proposal modifies editable fields only
- ✅ Update proposal blocks read-only field changes
- ✅ Proposal deleted after successful save

---

#### Task 5.2: Integration Tests
**File**: `tests/integration/test_validate_and_add_workflow.py`

**Test Cases**:
- ✅ End-to-end: Create proposal → Validate → Save → Verify in DB
- ✅ End-to-end: Create proposal → Reject → Verify deleted
- ✅ End-to-end: Create proposal with duplicate URL → Save fails
- ✅ End-to-end: Update proposal → Save → Verify changes in DB

---

### **Phase 6: Documentation** (1 hour)

#### Task 6.1: Update ARCHITECTURE.md
- ✅ Document new service layer components
- ✅ Update development state (Spec 002 complete)
- ✅ Update test coverage statistics

#### Task 6.2: Create Usage Documentation
**File**: `specs/002-validate-and-add-radio-source/USAGE.md`

**Content**:
- How to view proposals
- How to edit proposal data
- How to save/reject proposals
- Security warning explanation
- Duplicate handling explanation

---

## 📊 Progress Tracking

### Implementation Checklist

- [x] **Phase 1**: Service Layer
  - [x] Task 1.1: ProposalValidationService
  - [x] Task 1.2: RadioSourceService
- [x] **Phase 2**: DTOs
  - [x] Task 2.1: Validation DTOs
- [x] **Phase 3**: Textual TUI
  - [x] Task 3.1: Proposal List View
  - [x] Task 3.2: Detail/Edit Screen
  - [x] Task 3.3: Save/Reject Actions
- [x] **Phase 4**: Database Tab
  - [x] Task 4.1: View Stream Types
  - [x] Task 4.2: View Radio Sources
  - [x] Task 4.3: Run Migration
- [x] **Phase 5**: Testing
  - [x] Task 5.1: Unit Tests
  - [x] Task 5.2: Integration Tests
- [x] **Phase 6**: Documentation
  - [x] Task 6.1: Update ARCHITECTURE.md
  - [x] Task 6.2: Create USAGE.md

---

## 🎯 Acceptance Criteria

### Must Have (MVP)
- ✅ View all proposals in TUI
- ✅ Edit user-editable fields
- ✅ Save proposal to RadioSourceNode
- ✅ Reject/delete proposal
- ✅ Duplicate URL detection
- ✅ Security warning for HTTP streams
- ✅ Required field validation
- ✅ Unit tests with >80% coverage

### Should Have
- ✅ Proposal update functionality
- ✅ View saved radio sources
- ✅ View stream types
- ✅ Integration tests

### Nice to Have
- ⚠️ Search/filter radio sources
- ⚠️ Export radio sources to JSON
- ⚠️ Bulk proposal operations
- ⚠️ Proposal statistics dashboard

---

## 🔗 Dependencies

### External Dependencies
- None (all dependencies already in requirements.txt)

### Internal Dependencies
- ✅ Spec 003: Stream Analysis Service (completed)
- ✅ Database schema (completed)
- ✅ ProposalRepository (exists)
- ✅ RadioSourceRepository (exists)
- ⚠️ Spec 001: Discover workflow (for creating proposals) - can be simulated with manual DB inserts for testing

---

## 🧪 Testing Strategy

### Unit Testing
- Test each service method in isolation
- Mock database calls
- Test validation logic thoroughly
- Test error handling

### Integration Testing
- Test complete workflow with real database
- Test database transactions
- Test concurrent operations

### Manual Testing (via TUI)
- Create test proposals manually in database
- Test all UI interactions
- Test security warnings
- Test duplicate detection
- Test field validation

---

## 📝 Notes

### Design Decisions
1. **Security Warning**: Display as banner in edit screen + confirmation dialog on save for HTTP streams
2. **Duplicate Detection**: Check both proposals and radio_sources tables
3. **Proposal Deletion**: Delete proposal immediately after successful save (single transaction)
4. **Field Validation**: Validate on save, not on edit (better UX)
5. **Transaction Handling**: Use single transaction for save + delete proposal

### Known Limitations
1. No undo functionality for rejected proposals
2. No bulk operations in MVP
3. Image field accepts URL/path but doesn't validate image existence
4. No audit log for changes

### Future Enhancements
- Proposal versioning/history
- Collaborative validation (multi-user)
- Automated duplicate detection with fuzzy matching
- Image upload/preview functionality
- Batch import/export

---

**Last Updated**: November 24, 2025
**Status**: Ready for Implementation
**Estimated Total Time**: 15-22 hours (2-3 days)
