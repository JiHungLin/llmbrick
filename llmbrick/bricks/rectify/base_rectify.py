from llmbrick.core.brick import BaseBrick

class RectifyBrick(BaseBrick):
    """
    RectifyBrick: 基於 BaseBrick
    """
    grpc_service_type = "rectify"