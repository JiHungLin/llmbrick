from llmbrick.core.error_codes import ErrorCodes
from my_brick import MyIntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest
import asyncio

async def main():
    # 使用 toGrpcClient 建立遠端客戶端
    my_brick = MyIntentionBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )

    print("=== Get Service Info ===")
    try:
        service_info = await my_brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Normal Cases ===")
    # 測試不同意圖類型
    test_cases = [
        "你好，我有個問題",      # 預期: greet
        "help me please",       # 預期: help
        "我要查詢訂單資料",      # 預期: query
        "bye bye",             # 預期: goodbye
        "這是測試文本"          # 預期: unknown
    ]

    for text in test_cases:
        try:
            print(f"\nTesting text: {text}")
            request = IntentionRequest(text=text, client_id="grpc_client")
            response = await my_brick.run_unary(request)
            
            if response.error and response.error.code != ErrorCodes.SUCCESS:
                print(f"Error: {response.error.message}")
            else:
                result = response.results[0]
                print(f"Intent: {result.intent_category}")
                print(f"Confidence: {result.confidence}")
        except Exception as e:
            print(f"Error processing request: {e}")

    print("\n\n=== Error Cases ===")
    # 測試空文本
    try:
        print("\nTesting empty text:")
        request = IntentionRequest(text="", client_id="grpc_client")
        response = await my_brick.run_unary(request)
        print(f"Error (expected): {response.error.message}")
    except Exception as e:
        print(f"Error processing request: {e}")

    # 測試 None 文本
    try:
        print("\nTesting None text:")
        request = IntentionRequest(text=None, client_id="grpc_client")
        response = await my_brick.run_unary(request)
        print(f"Error (expected): {response.error.message}")
    except Exception as e:
        print(f"Error processing request: {e}")

if __name__ == "__main__":
    print("Connecting to gRPC server at 127.0.0.1:50051...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Client error: {e}")