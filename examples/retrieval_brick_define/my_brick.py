from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse, Document
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes

from typing import List, Optional

class MyRetrievalBrick(RetrievalBrick):
    """
    MyRetrievalBrick 是一個自訂的 RetrievalBrick 範例，支援查詢與服務資訊查詢。
    """

    def __init__(self, index_name: str = "default_index", default_docs: Optional[List[Document]] = None, **kwargs):
        super().__init__(**kwargs)
        self.index_name = index_name
        self.default_docs = default_docs or [
            Document(doc_id="1", title="Hello World", snippet="This is a demo document.", score=0.99),
            Document(doc_id="2", title="LLMBrick", snippet="RetrievalBrick example.", score=0.88),
        ]

    @unary_handler
    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        """
        處理檢索查詢，回傳文件列表。
        """
        if not request.query:
            return RetrievalResponse(
                documents=[],
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Query string is required."
                )
            )
        # 模擬查詢，實際應用可連接向量資料庫等
        docs = [
            Document(
                doc_id=f"{self.index_name}-{i+1}",
                title=f"Result {i+1} for '{request.query}'",
                snippet=f"Snippet for '{request.query}', doc {i+1}",
                score=1.0 - i * 0.1
            )
            for i in range(2)
        ]
        return RetrievalResponse(
            documents=docs,
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success"
            )
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        """
        回傳服務資訊。
        """
        return ServiceInfoResponse(
            service_name="MyRetrievalBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="retrieval-demo",
                    version="1.0",
                    supported_languages=["en", "zh"],
                    support_streaming=False,
                    description="A demo retrieval brick."
                )
            ],
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success"
            )
        )
