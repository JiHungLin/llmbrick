from llmbrick.core.brick import BaseBrick

class IntentionGuardBrick(BaseBrick):
    """
    IntentionGuardBrick: 基於 BaseBrick

    gRPC服務類型為'intention_guard'，用於意圖保護。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - CheckIntention: 用於檢查用戶意圖。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - CheckIntention -> unary

    """
    grpc_service_type = "intention_guard"