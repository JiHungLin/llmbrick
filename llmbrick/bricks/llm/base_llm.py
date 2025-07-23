from llmbrick.core.brick import BaseBrick

# gRPC Servicer class import
from llmbrick.protocols.grpc.llm import llm_pb2_grpc

class LLMBrick(BaseBrick):
    """
    LLMBrick: 基於 BaseBrick，並支援 default_prompt 參數
    """
    grpc_service_type = "llm"

    def __init__(self, default_prompt: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_prompt = default_prompt