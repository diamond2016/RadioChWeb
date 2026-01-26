from typing import Dict, List, Optional
from api.deps import get_db

from api.schemas.radio_source import RadioSourceListenMetadata, RadioSourceOut
from api.service.stream_type_api_service import StreamTypeAPIService
from model.entity.radio_source import RadioSource
from model.entity.radio_source import RadioSource
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.dto.radio_source import RadioSourceDTO
from model.repository.stream_type_repository import StreamTypeRepository
from service.auth_service import AuthService
from service.proposal_service import ProposalService
from service.radio_source_service import RadioSourceService
from service.stream_type_service import StreamTypeService

class RadioSourceAPIService:
     # Repository and service initialization functions
    def get_stream_type_repo(self) -> StreamTypeRepository:
        return StreamTypeRepository(get_db())
    def get_proposal_repo(self) -> ProposalRepository:
        return ProposalRepository(get_db())
    def get_radio_source_repo(self) -> RadioSourceRepository:
        return RadioSourceRepository(get_db())
    def get_auth_service(self) -> AuthService:
        return AuthService()
    def get_stream_type_service(self) -> StreamTypeService:
        return StreamTypeService(
            stream_type_repo=self.get_stream_type_repo()
        )
    def get_proposal_service(self) -> ProposalService:
        proposal_repo: ProposalRepository = self.get_proposal_repo()
        return ProposalService(
            proposal_repo=proposal_repo,
            radio_source_repo=self.get_radio_source_repo(),
            auth_service=self.get_auth_service(),
            stream_type_service=self.get_stream_type_service()
        )  
    def get_radio_source_service(self) -> RadioSourceService:
        return RadioSourceService(
            proposal_repo=self.get_proposal_repo(),
            radio_source_repo=self.get_radio_source_repo(),
            proposal_service=self.get_proposal_service(),
            auth_service=self.get_auth_service(),
            stream_type_service=self.get_stream_type_service()
        )
    def get_stream_type_api_service(self) -> StreamTypeAPIService:
        return StreamTypeAPIService()  
        
    def __init__(self):
        self.radio_source_service: RadioSourceService = self.get_radio_source_service()
        self.stream_type_api_service: StreamTypeAPIService = self.get_stream_type_api_service()


    def list_sources(self,
        q: str | None = None,
        stream_type: int | None = None,
        country: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[tuple[List[RadioSourceOut], int]]:
        """GET /api/v1/sources"""

        all_items: list[RadioSourceDTO] = self.radio_source_service.get_all_radio_sources()
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
        source: RadioSourceDTO = self.radio_source_service.get_radio_source(source_id)
        if not source:
            return None
        return RadioSourceOut.model_validate(source)

    def get_listen_metadata(self, source_id: int) -> Optional[RadioSourceListenMetadata]:
        source: RadioSourceDTO = self.radio_source_service.get_radio_source(source_id)
        if not source:
            return None
        return RadioSourceListenMetadata.model_validate({
            "stream_url": source.stream_url,
            "stream_type": self.stream_type_api_service.get_stream_type(source.stream_type),
            "name": source.name,
        })


# API Endpoints Summary



GET /api/v1/search
Convenience endpoint; maps to /sources?q=...
Optional Phase‑1 extras

