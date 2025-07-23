from llmbrick.servers.grpc.wrappers.llm_grpc_wrapper import LLMGrpcWrapper
from llmbrick.servers.grpc.wrappers.common_grpc_wrapper import CommonGrpcWrapper

_WRAPPER_MAP = {
    "llm": LLMGrpcWrapper,
    "common": CommonGrpcWrapper,
    # 之後可擴充 "rectify": RectifyGrpcWrapper, ...
}

def register_to_grpc_server(server, brick):
    service_type = getattr(brick.__class__, "grpc_service_type", "common")
    wrapper_cls = _WRAPPER_MAP.get(service_type, CommonGrpcWrapper)
    wrapper_cls(brick).register(server)