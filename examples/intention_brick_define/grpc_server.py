from my_brick import MyIntentionBrick
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

# 建立 gRPC 伺服器實例
grpc_server = GrpcServer(port=50051)

# 初始化 IntentionBrick
my_brick = MyIntentionBrick(
    model_name="grpc_demo_model",
    res_prefix="grpc_test",
    verbose=True  # 啟用詳細日誌以便於除錯
)

# 註冊服務
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()