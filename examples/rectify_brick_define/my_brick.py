from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes

class MyRectifyBrick(RectifyBrick):
    """
    MyRectifyBrick 是一個自訂的文本校正 Brick，繼承自 RectifyBrick。
    可自訂校正模式、支援語言等初始化參數。
    """

    def __init__(self, mode: str = "upper", supported_languages=None, description: str = "A simple rectify brick", **kwargs):
        """
        :param mode: 校正模式，預設 upper（可選 lower/reverse）
        :param supported_languages: 支援語言列表
        :param description: 服務描述
        """
        super().__init__(**kwargs)
        self.mode = mode
        self.supported_languages = supported_languages or ["en", "zh"]
        self.description = description

    @unary_handler
    async def rectify_handler(self, request: RectifyRequest) -> RectifyResponse:
        """
        處理單次文本校正請求。
        根據 mode 進行不同的校正處理。
        """
        text = request.text or ""
        if not text:
            return RectifyResponse(
                corrected_text="",
                error=ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            )

        if self.mode == "upper":
            corrected = text.upper()
        elif self.mode == "lower":
            corrected = text.lower()
        elif self.mode == "reverse":
            corrected = text[::-1]
        else:
            corrected = text

        return RectifyResponse(
            corrected_text=corrected,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """
        回傳服務資訊。
        """
        model_info_list = [
            ModelInfo(
                model_id="my_rectify_model",
                version="1.0",
                supported_languages=self.supported_languages,
                support_streaming=False,
                description=self.description
            )
        ]
        return ServiceInfoResponse(
            service_name="MyRectifyBrickService",
            version="1.0",
            models=model_info_list,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
