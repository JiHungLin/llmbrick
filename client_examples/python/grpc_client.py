"""
異步 gRPC 客戶端範例
展示如何使用 LLMBrick 和 CommonBrick 的異步 gRPC 客戶端功能
"""

import asyncio
from typing import AsyncIterator

from llmbrick.bricks.common.common import CommonBrick
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest
from llmbrick.protocols.models.bricks.llm_types import LLMRequest


async def test_llm_grpc_client() -> None:
    """測試 LLM gRPC 異步客戶端"""
    print("=== 測試 LLM gRPC 異步客戶端 ===")

    # 建立 gRPC 客戶端
    llm_client = LLMBrick.toGrpcClient(
        remote_address="127.0.0.1:50051", default_prompt="你是一個有用的助手。"
    )

    try:
        # 測試服務信息
        print("1. 獲取服務信息...")
        service_info = await llm_client.run_get_service_info()
        print(f"服務信息: {service_info}")

        # 測試單次請求
        print("\n2. 測試單次請求...")
        request = LLMRequest(prompt="什麼是人工智慧？", max_tokens=100, temperature=0.7)
        response = await llm_client.run_unary(request)
        print(f"回應: {response}")

        # 測試流式回應
        print("\n3. 測試流式回應...")
        stream_request = LLMRequest(
            prompt="請解釋機器學習的基本概念", max_tokens=200, temperature=0.8
        )
        print("流式回應:")
        async for chunk in llm_client.run_output_streaming(stream_request):
            print(f"  - {chunk}")

    except Exception as e:
        print(f"錯誤: {e}")


async def test_common_grpc_client() -> None:
    """測試 Common gRPC 異步客戶端"""
    print("\n=== 測試 Common gRPC 異步客戶端 ===")

    # 建立 gRPC 客戶端
    common_client = CommonBrick.toGrpcClient(remote_address="127.0.0.1:50052")

    try:
        # 測試服務信息
        print("1. 獲取服務信息...")
        service_info = await common_client.run_get_service_info()
        print(f"服務信息: {service_info}")

        # 測試單次請求
        print("\n2. 測試單次請求...")
        request = CommonRequest(data={"message": "Hello from async gRPC client!"})
        response = await common_client.run_unary(request)
        print(f"回應: {response}")

        # 測試流式回應
        print("\n3. 測試流式回應...")
        stream_request = CommonRequest(data={"message": "Stream test", "count": 5})
        print("流式回應:")
        async for chunk in common_client.run_output_streaming(stream_request):
            print(f"  - {chunk}")

        # 測試流式輸入
        print("\n4. 測試流式輸入...")

        async def input_generator() -> AsyncIterator[CommonRequest]:
            for i in range(3):
                yield CommonRequest(data={"index": i, "message": f"Input {i}"})
                await asyncio.sleep(0.1)

        input_response = await common_client.run_input_streaming(input_generator())
        print(f"流式輸入回應: {input_response}")

        # 測試雙向流式
        print("\n5. 測試雙向流式...")

        async def bidi_generator() -> AsyncIterator[CommonRequest]:
            for i in range(3):
                yield CommonRequest(data={"bidi_index": i, "message": f"Bidi {i}"})
                await asyncio.sleep(0.1)

        print("雙向流式回應:")
        async for chunk in common_client.run_bidi_streaming(bidi_generator()):
            print(f"  - {chunk}")

    except Exception as e:
        print(f"錯誤: {e}")


async def main() -> None:
    """主函數"""
    print("異步 gRPC 客戶端測試開始...")

    # 測試 LLM 客戶端
    await test_llm_grpc_client()

    # 測試 Common 客戶端
    await test_common_grpc_client()

    print("\n測試完成！")


if __name__ == "__main__":
    # 運行異步主函數
    asyncio.run(main())
