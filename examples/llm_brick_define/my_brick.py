from typing import List, AsyncIterator
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, Context
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler

class MyLLMBrick(LLMBrick):
    """
    MyLLMBrick 是 LLMBrick 的自訂範例，展示 echo、流式回應與服務資訊查詢。
    支援 default_prompt、model_id、supported_languages、version、description 等初始化參數。
    """

    def __init__(
        self,
        default_prompt: str = "Say something",
        model_id: str = "my-llm-model",
        supported_languages: List[str] = None,
        version: str = "1.0.0",
        description: str = "A simple LLMBrick example that echoes prompt and streams output.",
        **kwargs
    ):
        super().__init__(default_prompt=default_prompt, **kwargs)
        self.model_id = model_id
        self.supported_languages = supported_languages or ["en", "zh"]
        self.version = version
        self.description = description

    @unary_handler
    async def echo(self, request: LLMRequest) -> LLMResponse:
        """
        單次請求-回應：回傳 prompt 或 default_prompt，tokens 為字串列表。
        """
        prompt = request.prompt or self.default_prompt
        if not isinstance(request.context, list):
            error = ErrorDetail(
                code=ErrorCodes.PARAMETER_INVALID,
                message="context 必須為 List[Context]"
            )
            return LLMResponse(text="", tokens=[], is_final=True, error=error)
        if not prompt:
            error = ErrorDetail(
                code=ErrorCodes.PARAMETER_INVALID,
                message="prompt 不可為空"
            )
            return LLMResponse(text="", tokens=[], is_final=True, error=error)
        # tokens 必須為 List[str]
        tokens = prompt.split()
        return LLMResponse(
            text=f"Echo: {prompt}",
            tokens=tokens,
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @output_streaming_handler
    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMResponse]:
        """
        單次請求-流式回應：將 prompt 拆成多段流式回傳。
        """
        prompt = request.prompt or self.default_prompt
        if not prompt:
            yield LLMResponse(
                text="",
                tokens=[],
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="prompt 不可為空")
            )
            return
        words = prompt.split()
        for idx, word in enumerate(words):
            yield LLMResponse(
                text=word,
                tokens=[word],
                is_final=(idx == len(words) - 1),
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        """
        回傳本 Brick 的服務資訊。
        """
        model_info = ModelInfo(
            model_id=self.model_id,
            version=self.version,
            supported_languages=self.supported_languages,
            support_streaming=True,
            description=self.description
        )
        return ServiceInfoResponse(
            service_name="MyLLMBrick",
            version=self.version,
            models=[model_info],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
