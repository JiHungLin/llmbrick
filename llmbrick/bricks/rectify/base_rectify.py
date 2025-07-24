from llmbrick.core.brick import BaseBrick

class RectifyBrick(BaseBrick):
    """
    RectifyBrick: 基於 BaseBrick

    gRPC服務類型為'rectify'，用於文本校正。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - RectifyText: 用於校正文本。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - RectifyText -> unary
    """
    grpc_service_type = "rectify"