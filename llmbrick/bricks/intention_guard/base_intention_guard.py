from llmbrick.core.brick import BaseBrick

class IntentionGuardBrick(BaseBrick):
    """
    IntentionGuardBrick: 基於 BaseBrick
    """
    grpc_service_type = "intention_guard"