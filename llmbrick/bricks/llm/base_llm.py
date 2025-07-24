from llmbrick.core.brick import BaseBrick

# gRPC Servicer class import
from llmbrick.protocols.grpc.llm import llm_pb2_grpc

class LLMBrick(BaseBrick):
    """
    LLMBrick: 基於 BaseBrick，並支援 default_prompt 參數
    
    gRPC服務類型為'llm'，用於處理大型語言模型相關請求。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - GenerateResponse: 用於生成模型回應。
    - GenerateResponseStream: 用於生成模型回應的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - GenerateResponse -> unary
    - GenerateResponseStream -> output_streaming

    """
    grpc_service_type = "llm"

    def __init__(self, default_prompt: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_prompt = default_prompt