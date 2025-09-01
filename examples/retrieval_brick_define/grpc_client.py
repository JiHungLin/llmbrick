from my_brick import MyRetrievalBrick
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest

if __name__ == "__main__":
    import asyncio

    # 建立 gRPC client
    my_brick = MyRetrievalBrick.toGrpcClient(remote_address="127.0.0.1:50051")

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            info = await my_brick.run_get_service_info()
            print(info)
        asyncio.run(example())

    run_get_service_info_example()

    print("\n=== Unary Method ===")
    def run_unary_example(is_test_error=False):
        async def example():
            if is_test_error:
                req = RetrievalRequest(query="", client_id="cid")
            else:
                req = RetrievalRequest(query="test query", client_id="cid")
            resp = await my_brick.run_unary(req)
            print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case (empty query):")
    run_unary_example(is_test_error=True)
