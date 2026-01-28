from typing import List, Optional, Any
from deps import get_db_session

# Avoid importing heavy application modules at import time. Import them lazily
# inside methods to keep this module safe to import from the main venv.
from api.schemas.radio_source import RadioSourceList, RadioSourceListenMetadata, RadioSourceOut
from model.entity.radio_source import RadioSource
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.repository.stream_type_repository import StreamTypeRepository
from service.auth_service import AuthService
from service.radio_source_service import RadioSourceService
from service.stream_type_service import StreamTypeService
from service.proposal_service import ProposalService

class RadioSourceAPIService:
    """API-facing service for radio sources.

    Supports dependency injection: callers may pass pre-built service instances
    to the constructor to avoid importing application internals at module
    import time. When dependencies are not provided they are created lazily
    using local imports.
    """

    def __init__(self): 
        self._radio_source_service: RadioSourceService = self.get_radio_source_service()

    # Repository and service initialization functions (lazily imported)
    def get_stream_type_repo(self) -> StreamTypeRepository:
        from model.repository.stream_type_repository import StreamTypeRepository
        return StreamTypeRepository(get_db_session())

    def get_proposal_repo(self) -> ProposalRepository:
        from model.repository.proposal_repository import ProposalRepository
        return ProposalRepository(get_db_session())

    def get_radio_source_repo(self) -> RadioSourceRepository:
        from model.repository.radio_source_repository import RadioSourceRepository
        return RadioSourceRepository(get_db_session())

    def get_auth_service(self) -> AuthService:
        from service.auth_service import AuthService
        return AuthService()

    def get_stream_type_service(self) -> StreamTypeService:
        from service.stream_type_service import StreamTypeService
        return StreamTypeService(stream_type_repository=self.get_stream_type_repo())

    def get_proposal_service(self) -> ProposalService:
        return ProposalService(self.get_proposal_repo())

    def get_radio_source_service(self) -> RadioSourceService:
        return RadioSourceService(
            proposal_repo=self.get_proposal_repo(),
            radio_source_repo=self.get_radio_source_repo(),
            proposal_service=self.get_proposal_service(),
            auth_service=self.get_auth_service(),
            stream_type_service=self.get_stream_type_service()
        )
            
    def get_all_radio_sources(self) -> RadioSourceList:
        """GET /api/v1/sources/all"""
        all_items: List[RadioSource] = self._radio_source_service.get_all_radio_sources()
        if not all_items:
            return RadioSourceList(items=[], total=0, page=1, page_size=0)
        
        # prepare out for API (RadioSourceOut)
        all_items_out: List[RadioSourceOut] = [RadioSourceOut.model_validate(item) for item in all_items]
        return RadioSourceList(items=all_items_out, total=len(all_items_out), page=1, page_size=len(all_items_out))


    def list_sources(self,
        q: str | None = None,
        stream_type: int | None = None,
        country: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[tuple[List[RadioSourceOut], int]]:
        """GET /api/v1/sources"""

        all_items: List[RadioSource] = self._radio_source_service.get_all_radio_sources()
        if not all_items:
            return None
        
        if q:
            all_items = [item for item in all_items if q.lower() in item.name.lower()]
        if stream_type:
            all_items = [item for item in all_items if item.stream_type.id == stream_type]
        if country:
            all_items = [item for item in all_items if item.country == country]
        total = len(all_items)
        start = (page - 1) * page_size
        end = start + page_size

        # prepare out for API (RadioSourceOut)
        all_items_out: List[RadioSourceOut] = [RadioSourceOut.model_validate(item) for item in all_items]
        paged_items: List[RadioSourceOut] = all_items_out[start:end]  
        return paged_items, total


    def get_source(self, source_id: int) -> Optional[RadioSourceOut]:
        """GET /api/v1/sources/{id}"""
        source: Any = self._radio_source_service.get_radio_source_by_id(source_id)
        if not source:
            return None
        return RadioSourceOut.model_validate(source)

    def get_listen_metadata(self, source_id: int) -> Optional[RadioSourceListenMetadata]:
        source: Any = self._radio_source_service.get_radio_source_by_id(source_id)
        if not source:
            return None
        return RadioSourceListenMetadata.model_validate({
            "source_id": source.id,
            "stream_url": source.stream_url,
            "stream_type": self.get_stream_type_service().get_stream_type(source.stream_type),
            "name": source.name
        })

