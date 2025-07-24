from llmbrick.core.brick import BaseBrick

class ComposeTranslateBrick(BaseBrick):
    """
    ComposeTranslateBrick: 基於 BaseBrick

    gRPC服務類型為'ComposeTranslate'，用於統整資料、轉換或翻譯。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - ComposeAndTranslate: 用於統整資料並進行翻譯。
    - ComposeAndTranslateStream: 用於統整資料並進行翻譯的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - ComposeAndTranslate -> unary
    - ComposeAndTranslateStream -> output_streaming

    """
    grpc_service_type = "ComposeTranslate"