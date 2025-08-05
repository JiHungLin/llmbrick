from typing import AsyncIterator
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo,
)
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)


class MyTranslateBrick(TranslateBrick):
    """
    MyTranslateBrick is a custom TranslateBrick implementation for demonstration.
    It supports unary, output streaming, and service info handlers only.
    """

    def __init__(
        self,
        model_name: str = "my_translate_model",
        default_target_language: str = "zh",
        verbose: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.default_target_language = default_target_language
        self.verbose = verbose

    @unary_handler
    async def unary_translate(self, request: TranslateRequest) -> TranslateResponse:
        """
        A unary translation method. Returns a simple echo translation.
        """
        text = request.text or ""
        target_lang = request.target_language or self.default_target_language
        if not text:
            return TranslateResponse(
                text="",
                tokens=[],
                language_code=target_lang,
                is_final=True,
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Input text is required.",
                ),
            )
        # Echo translation (for demo)
        return TranslateResponse(
            text=f"{text} (to {target_lang})",
            tokens=[1, 2, 3],
            language_code=target_lang,
            is_final=True,
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success",
            ),
        )

    @output_streaming_handler
    async def stream_translate(self, request: TranslateRequest) -> AsyncIterator[TranslateResponse]:
        """
        Output streaming translation. Yields each word as a translated chunk.
        """
        text = request.text or ""
        target_lang = request.target_language or self.default_target_language
        if not text:
            yield TranslateResponse(
                text="",
                tokens=[],
                language_code=target_lang,
                is_final=True,
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Input text is required.",
                ),
            )
            return

        words = text.split()
        for i, word in enumerate(words):
            yield TranslateResponse(
                text=f"{word} (t{i})",
                tokens=[i],
                language_code=target_lang,
                is_final=(i == len(words) - 1),
                error=ErrorDetail(
                    code=ErrorCodes.SUCCESS,
                    message="Success",
                ),
            )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        """
        Returns service information for this TranslateBrick.
        """
        model_info = ModelInfo(
            model_id=self.model_name,
            version="1.0",
            supported_languages=["en", "zh"],
            support_streaming=True,
            description="A demo translation model that echoes input text.",
        )
        return ServiceInfoResponse(
            service_name="MyTranslateBrickService",
            version="1.0",
            models=[model_info],
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success",
            ),
        )