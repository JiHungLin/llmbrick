from llmbrick.core.brick import BaseBrick

class RetrievalBrick(BaseBrick):
    """
    RetrievalBrick: 基於 BaseBrick

    gRPC服務類型為'retrieval'，用於檢索相關信息。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - RetrieveData: 用於檢索數據。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - RetrieveData -> unary

    """
    grpc_service_type = "retrieval"