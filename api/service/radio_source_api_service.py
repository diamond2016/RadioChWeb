from typing import List, Optional, Any
from deps import get_db_session

# Avoid importing heavy application modules at import time. Import them lazily
# inside methods to keep this module safe to import from the main venv.
from api.schemas.radio_source import RadioSourceListenMetadata, RadioSourceOut

class RadioSourceAPIService:
    """API-facing service for radio sources.

    Supports dependency injection: callers may pass pre-built service instances
    to the constructor to avoid importing application internals at module
    import time. When dependencies are not provided they are created lazily
    using local imports.
    """

    def __init__(
        self,
        radio_source_service: Optional[Any] = None,
        stream_type_api_service: Optional[Any] = None,
    ):
        self._radio_source_service = radio_source_service
        self._stream_type_api_service = stream_type_api_service

    # Repository and service initialization functions (lazily imported)
    def get_stream_type_repo(self):
        from model.repository.stream_type_repository import StreamTypeRepository

        return StreamTypeRepository(get_db_session())

    def get_proposal_repo(self):
        from model.repository.proposal_repository import ProposalRepository

        return ProposalRepository(get_db_session())

    def get_radio_source_repo(self):
        from model.repository.radio_source_repository import RadioSourceRepository

        return RadioSourceRepository(get_db_session())

    def get_auth_service(self):
        from service.auth_service import AuthService

        return AuthService()

    def get_stream_type_service(self):
        from service.stream_type_service import StreamTypeService

        return StreamTypeService(stream_type_repo=self.get_stream_type_repo())

    def get_proposal_service(self):
        from service.proposal_service import ProposalService

        proposal_repo = self.get_proposal_repo()
        return ProposalService(
            proposal_repo=proposal_repo,
            radio_source_repo=self.get_radio_source_repo(),
            auth_service=self.get_auth_service(),
            stream_type_service=self.get_stream_type_service(),
        )

    def get_radio_source_service(self):
        # If injected, return it
        if self._radio_source_service is not None:
            return self._radio_source_service

        from service.radio_source_service import RadioSourceService

        svc = RadioSourceService(
            proposal_repo=self.get_proposal_repo(),
            radio_source_repo=self.get_radio_source_repo(),
            proposal_service=self.get_proposal_service(),
            auth_service=self.get_auth_service(),
            stream_type_service=self.get_stream_type_service(),
        )
        self._radio_source_service = svc
        return svc

    def get_stream_type_api_service(self):
        if self._stream_type_api_service is not None:
            return self._stream_type_api_service
        from api.service.stream_type_api_service import StreamTypeAPIService

        svc = StreamTypeAPIService()
        self._stream_type_api_service = svc
        return svc


    def list_sources(self,
        q: str | None = None,
        stream_type: int | None = None,
        country: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[tuple[List[RadioSourceOut], int]]:
        """GET /api/v1/sources"""

        all_items: list = self.get_radio_source_service().get_all_radio_sources()
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
        source: Any = self.get_radio_source_service().get_radio_source(source_id)
        if not source:
            return None
        return RadioSourceOut.model_validate(source)

    def get_listen_metadata(self, source_id: int) -> Optional[RadioSourceListenMetadata]:
        source: Any = self.get_radio_source_service().get_radio_source(source_id)
        if not source:
            return None
        return RadioSourceListenMetadata.model_validate({
            "stream_url": source.stream_url,
            "stream_type": self.get_stream_type_api_service().get_stream_type(source.stream_type),
            "name": source.name,
        })

