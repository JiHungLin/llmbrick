from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from typing import Optional
from llmbrick.core.error_codes import ErrorCodes


class MyGuardBrick(GuardBrick):
    """
    MyGuardBrick 是一個自訂的 GuardBrick 範例，僅支援 unary 與 get_service_info 兩種 handler。
    可自訂靈敏度(sensitivity)與 verbose 參數。
    """

    def __init__(self, sensitivity: float = 0.5, verbose: bool = False, **kwargs):
        """
        :param sensitivity: 攻擊偵測靈敏度 (0~1)
        :param verbose: 是否輸出詳細日誌
        """
        super().__init__(**kwargs)
        self.sensitivity = sensitivity
        self.verbose = verbose

    @unary_handler
    async def check(self, request: GuardRequest) -> GuardResponse:
        """
        檢查輸入文字是否為攻擊，並回傳 GuardResponse。
        """
        try:
            text = (request.text or "").lower()
            is_attack = "attack" in text or "攻擊" in text
            confidence = 0.99 if is_attack else 0.1
            detail = "Detected attack" if is_attack else "Safe"
            # 根據 sensitivity 調整判斷
            if is_attack and confidence < self.sensitivity:
                is_attack = False
                detail = "Below sensitivity threshold"
            result = GuardResult(
                is_attack=is_attack,
                confidence=confidence,
                detail=detail
            )
            if self.verbose:
                print(f"[MyGuardBrick] Input: {text}, is_attack: {is_attack}, confidence: {confidence}, detail: {detail}")
            return GuardResponse(
                results=[result],
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
        except Exception as e:
            return GuardResponse(
                results=[],
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message="Internal error", detail=str(e))
            )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        """
        回傳服務資訊。
        """
        return ServiceInfoResponse(
            service_name="MyGuardBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message=f"Sensitivity: {self.sensitivity}, Verbose: {self.verbose}")
        )
