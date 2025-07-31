from llmbrick.servers.grpc.wrappers.common_grpc_wrapper import CommonGrpcWrapper
from llmbrick.servers.grpc.wrappers.compose_grpc_wrapper import ComposeGrpcWrapper
from llmbrick.servers.grpc.wrappers.guard_grpc_wrapper import GuardGrpcWrapper
from llmbrick.servers.grpc.wrappers.intention_grpc_wrapper import IntentionGrpcWrapper
from llmbrick.servers.grpc.wrappers.llm_grpc_wrapper import LLMGrpcWrapper
from llmbrick.servers.grpc.wrappers.rectify_grpc_wrapper import RectifyGrpcWrapper
from llmbrick.servers.grpc.wrappers.retrieval_grpc_wrapper import RetrievalGrpcWrapper
from llmbrick.servers.grpc.wrappers.translate_grpc_wrapper import TranslateGrpcWrapper

_WRAPPER_MAP = {
    "LLM": LLMGrpcWrapper,
    "Common": CommonGrpcWrapper,
    "Compose": ComposeGrpcWrapper,
    "Guard": GuardGrpcWrapper,
    "Intention": IntentionGrpcWrapper,
    "Rectify": RectifyGrpcWrapper,
    "Retrieval": RetrievalGrpcWrapper,
    "Translate": TranslateGrpcWrapper,
}


def register_to_grpc_server(server, brick):
    service_type = getattr(brick.__class__, "brick_type", "Common")
    # 若是 Enum，取 value；否則直接用
    if hasattr(service_type, "value"):
        service_type_key = service_type.value
    else:
        service_type_key = service_type
    wrapper_cls = _WRAPPER_MAP.get(service_type_key, CommonGrpcWrapper)
    wrapper_cls(brick).register(server)
