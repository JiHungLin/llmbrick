import asyncio
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest
from my_brick import MyRetrievalBrick

async def main():
    brick = MyRetrievalBrick(index_name="local_index")
    print("=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        print("Normal case:")
        req = RetrievalRequest(query="test query", client_id="cid")
        resp = await brick.run_unary(req)
        print(resp)

        print("\nError case (empty query):")
        req = RetrievalRequest(query="", client_id="cid")
        resp = await brick.run_unary(req)
        print(resp)
    except Exception as e:
        print(f"Error in unary call: {e}")

if __name__ == "__main__":
    asyncio.run(main())