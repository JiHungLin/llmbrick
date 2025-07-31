"""
異步 gRPC 伺服器範例
展示如何使用異步 GrpcServer 啟動 LLM 和 Common 服務
"""

import asyncio
from typing import Any, AsyncIterator

from llmbrick.bricks.common.common import CommonBrick
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse
from llmbrick.servers.grpc.server import GrpcServer


class ExampleLLMBrick(LLMBrick):
    """範例 LLM Brick 實作"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(default_prompt="你是一個有用的 AI 助手。", **kwargs)

    async def unary_handler(self, request: LLMRequest) -> LLMResponse:
        """處理單次 LLM 請求"""
        prompt = request.prompt or self.default_prompt
        # 模擬 LLM 處理
        response_text = f"[模擬回應] 針對提示 '{prompt}' 的回應"

        return LLMResponse(
            text=response_text,
            tokens=list(response_text),
            is_final=True,
            error=None,
        )

    async def output_streaming_handler(
        self, request: LLMRequest
    ) -> AsyncIterator[LLMResponse]:
        """處理流式 LLM 請求"""
        prompt = request.prompt or self.default_prompt
        words = f"[流式回應] 針對 '{prompt}' 的逐字回應".split()

        for i, word in enumerate(words):
            await asyncio.sleep(0.1)  # 模擬處理延遲
            yield LLMResponse(
                text=word,
                tokens=[word],
                is_final=(i == len(words) - 1),
                error=None,
            )


class ExampleCommonBrick(CommonBrick):
    """範例 Common Brick 實作"""

    async def unary_handler(self, request: CommonRequest) -> CommonResponse:
        """處理單次通用請求"""
        data = request.data or {}
        response_data = {
            "echo": data,
            "timestamp": asyncio.get_event_loop().time(),
            "message": "Hello from async Common Brick!",
        }

        return CommonResponse(data=response_data)

    async def output_streaming_handler(
        self, request: CommonRequest
    ) -> AsyncIterator[CommonResponse]:
        """處理流式輸出"""
        count = request.data.get("count", 3) if request.data else 3

        for i in range(count):
            await asyncio.sleep(0.2)
            yield CommonResponse(
                data={"index": i, "message": f"Stream message {i + 1}", "total": count}
            )

    async def input_streaming_handler(
        self, request_stream: AsyncIterator[CommonRequest]
    ) -> CommonResponse:
        """處理流式輸入"""
        messages = []
        async for request in request_stream:
            if request.data:
                messages.append(request.data)

        return CommonResponse(
            data={
                "received_count": len(messages),
                "messages": messages,
                "summary": "Input streaming completed",
            }
        )

    async def bidi_streaming_handler(
        self, request_stream: AsyncIterator[CommonRequest]
    ) -> AsyncIterator[CommonResponse]:
        """處理雙向流式"""
        async for request in request_stream:
            if request.data:
                # 回應每個輸入
                yield CommonResponse(
                    data={
                        "echo": request.data,
                        "processed_at": asyncio.get_event_loop().time(),
                    }
                )


async def start_llm_server() -> None:
    """啟動 LLM gRPC 伺服器"""
    print("啟動 LLM gRPC 伺服器...")

    # 建立 LLM Brick
    llm_brick = ExampleLLMBrick()

    # 建立並配置伺服器
    server = GrpcServer(port=50051)
    server.register_service(llm_brick)

    # 啟動伺服器
    await server.start()


async def start_common_server() -> None:
    """啟動 Common gRPC 伺服器"""
    print("啟動 Common gRPC 伺服器...")

    # 建立 Common Brick
    common_brick = ExampleCommonBrick()

    # 建立並配置伺服器
    server = GrpcServer(port=50052)
    server.register_service(common_brick)

    # 啟動伺服器
    await server.start()


async def start_combined_server() -> None:
    """啟動組合 gRPC 伺服器（同時提供 LLM 和 Common 服務）"""
    print("啟動組合 gRPC 伺服器...")

    # 建立 Brick 實例
    llm_brick = ExampleLLMBrick()
    common_brick = ExampleCommonBrick()

    # 建立並配置伺服器
    server = GrpcServer(port=50053)
    server.register_service(llm_brick)
    server.register_service(common_brick)

    print("組合伺服器已啟動，同時提供 LLM 和 Common 服務")

    # 啟動伺服器
    await server.start()


async def main() -> None:
    """主函數"""
    import sys

    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python async_grpc_server.py llm      # 啟動 LLM 伺服器")
        print("  python async_grpc_server.py common   # 啟動 Common 伺服器")
        print("  python async_grpc_server.py combined # 啟動組合伺服器")
        return

    server_type = sys.argv[1].lower()

    try:
        if server_type == "llm":
            await start_llm_server()
        elif server_type == "common":
            await start_common_server()
        elif server_type == "combined":
            await start_combined_server()
        else:
            print(f"未知的伺服器類型: {server_type}")

    except KeyboardInterrupt:
        print("\n收到中斷信號，正在關閉伺服器...")
    except Exception as e:
        print(f"伺服器錯誤: {e}")


if __name__ == "__main__":
    # 運行異步主函數
    asyncio.run(main())
