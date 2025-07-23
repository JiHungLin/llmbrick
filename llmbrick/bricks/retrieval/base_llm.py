from llmbrick.core.brick import BaseBrick

class RetrievalBrick(BaseBrick):
    """
    RetrievalBrick: 基於 BaseBrick
    """
    grpc_service_type = "retrieval"