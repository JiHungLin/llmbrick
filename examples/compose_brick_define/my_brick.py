from typing import AsyncIterator
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from llmbrick.core.error_codes import ErrorCodes

from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler

class MyComposeBrick(ComposeBrick):
    """
    MyComposeBrick 是一個自訂的 ComposeBrick 範例，展示 unary、output_streaming、get_service_info 三種模式。
    支援自訂描述前綴(desc_prefix)與預設格式(default_format)。
    """

    def __init__(self, desc_prefix: str = "ComposeResult", default_format: str = "json", **kwargs):
        """
        :param desc_prefix: 回應內容的描述前綴
        :param default_format: 預設輸出格式
        """
        super().__init__(**kwargs)
        self.desc_prefix = desc_prefix
        self.default_format = default_format

    @unary_handler
    async def unary_process(self, request: ComposeRequest) -> ComposeResponse:
        try:
            count = len(request.input_documents)
            fmt = request.target_format or self.default_format
            return ComposeResponse(
                output={
                    "desc": f"{self.desc_prefix}: 共 {count} 筆文件, 格式: {fmt}",
                    "count": count,
                    "format": fmt
                },
                error=ErrorDetail(code=ErrorCodes, message="Success")
            )
        except Exception as e:
            return ComposeResponse(
                output={},
                error=ErrorDetail(code=1, message=f"Error: {e}")
            )

    @output_streaming_handler
    async def stream_titles(self, request: ComposeRequest) -> AsyncIterator[ComposeResponse]:
        try:
            for idx, doc in enumerate(request.input_documents):
                yield ComposeResponse(
                    output={
                        "desc": f"{self.desc_prefix}: 第{idx+1}筆",
                        "index": idx,
                        "title": getattr(doc, "title", ""),
                        "format": request.target_format or self.default_format
                    },
                    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
                )
        except Exception as e:
            yield ComposeResponse(
                output={},
                error=ErrorDetail(code=ErrorCodes.UNKNOWN_ERROR, message=f"Error: {e}")
            )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="MyComposeBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.UNKNOWN_ERROR, message=f"Default format: {self.default_format}, Desc prefix: {self.desc_prefix}")
        )
