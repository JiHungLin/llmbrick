"""
異步 gRPC 功能測試
測試伺服器和客戶端的異步功能是否正常工作
"""
import asyncio
import time
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse


class TestLLMBrick(LLMBrick):
    """測試用的 LLM Brick"""
    
    def __init__(self, **kwargs):
        super().__init__(default_prompt="測試助手", **kwargs)
    
    async def unary_handler(self, request: LLMRequest) -> LLMResponse:
        """測試單次請求處理"""
        await asyncio.sleep(0.1)  # 模擬處理時間
        return LLMResponse(
            text=f"回應: {request.prompt}",
            tokens_used=10,
            model="test-llm"
        )
    
    async def output_streaming_handler(self, request: LLMRequest):
        """測試流式輸出"""
        words = ["這", "是", "流式", "回應"]
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)
            yield LLMResponse(
                text=word,
                tokens_used=i + 1,
                model="test-llm",
                is_final=(i == len(words) - 1)
            )


class TestCommonBrick(CommonBrick):
    """測試用的 Common Brick"""
    
    async def unary_handler(self, request: CommonRequest) -> CommonResponse:
        """測試單次請求處理"""
        await asyncio.sleep(0.1)
        return CommonResponse(data={
            "echo": request.data,
            "processed": True
        })
    
    async def output_streaming_handler(self, request: CommonRequest):
        """測試流式輸出"""
        count = request.data.get("count", 3) if request.data else 3
        for i in range(count):
            await asyncio.sleep(0.05)
            yield CommonResponse(data={
                "index": i,
                "message": f"Stream {i}"
            })


async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    print("測試異步 gRPC 伺服器啟動...")
    
    # 建立測試 Brick
    llm_brick = TestLLMBrick()
    
    # 建立伺服器
    server = GrpcServer(port=50054)
    server.register_service(llm_brick)
    
    # 測試伺服器建立
    assert server.server is not None
    assert server.port == 50054
    
    print("✓ 伺服器建立成功")


async def test_llm_grpc_client():
    """測試 LLM gRPC 客戶端功能"""
    print("測試 LLM gRPC 客戶端...")
    
    # 啟動測試伺服器
    llm_brick = TestLLMBrick()
    server = GrpcServer(port=50055)
    server.register_service(llm_brick)
    
    # 在背景啟動伺服器
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)  # 等待伺服器啟動
    
    try:
        # 建立客戶端
        client_brick = LLMBrick.toGrpcClient(
            remote_address="127.0.0.1:50055",
            default_prompt="測試客戶端"
        )
        
        # 測試單次請求
        request = LLMRequest(prompt="測試提示")
        response = await client_brick.run_unary(request)
        
        assert response is not None
        assert "測試提示" in response.text
        print("✓ 單次請求測試通過")
        
        # 測試流式請求
        stream_responses = []
        async for chunk in client_brick.run_output_streaming(request):
            stream_responses.append(chunk)
        
        assert len(stream_responses) > 0
        print(f"✓ 流式請求測試通過，收到 {len(stream_responses)} 個回應")
        
        # 清理客戶端
        await client_brick._grpc_channel.close()
        
    finally:
        # 停止伺服器
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def test_common_grpc_client():
    """測試 Common gRPC 客戶端功能"""
    print("測試 Common gRPC 客戶端...")
    
    # 啟動測試伺服器
    common_brick = TestCommonBrick()
    server = GrpcServer(port=50056)
    server.register_service(common_brick)
    
    # 在背景啟動伺服器
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)  # 等待伺服器啟動
    
    try:
        # 建立客戶端
        client_brick = CommonBrick.toGrpcClient(remote_address="127.0.0.1:50056")
        
        # 測試單次請求
        request = CommonRequest(data={"test": "data"})
        response = await client_brick.run_unary(request)
        
        assert response is not None
        assert response.data["processed"] is True
        print("✓ Common 單次請求測試通過")
        
        # 測試流式請求
        stream_request = CommonRequest(data={"count": 2})
        stream_responses = []
        async for chunk in client_brick.run_output_streaming(stream_request):
            stream_responses.append(chunk)
        
        assert len(stream_responses) == 2
        print(f"✓ Common 流式請求測試通過，收到 {len(stream_responses)} 個回應")
        
        # 清理客戶端
        await client_brick._grpc_channel.close()
        
    finally:
        # 停止伺服器
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def test_performance():
    """測試異步性能"""
    print("測試異步性能...")
    
    # 啟動測試伺服器
    llm_brick = TestLLMBrick()
    server = GrpcServer(port=50057)
    server.register_service(llm_brick)
    
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    
    try:
        # 建立多個客戶端
        clients = []
        for i in range(3):
            client = LLMBrick.toGrpcClient(
                remote_address="127.0.0.1:50057",
                default_prompt=f"客戶端{i}"
            )
            clients.append(client)
        
        # 並發測試
        start_time = time.time()
        
        async def make_request(client, index):
            request = LLMRequest(prompt=f"並發請求 {index}")
            return await client.run_unary(request)
        
        # 同時發送多個請求
        tasks = [make_request(clients[i % len(clients)], i) for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert len(responses) == 5
        assert all(r is not None for r in responses)
        print(f"✓ 並發測試通過，5個請求耗時 {duration:.2f} 秒")
        
        # 清理客戶端
        for client in clients:
            await client._grpc_channel.close()
            
    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def run_all_tests():
    """運行所有測試"""
    print("開始異步 gRPC 功能測試...\n")
    
    tests = [
        test_async_grpc_server_startup,
        test_llm_grpc_client,
        test_common_grpc_client,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
            print(f"✓ {test.__name__} 通過\n")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} 失敗: {e}\n")
    
    print(f"測試結果: {passed} 通過, {failed} 失敗")
    return failed == 0


if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)