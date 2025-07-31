import time
from concurrent import futures
from typing import Any, AsyncIterator

import grpc
from google.protobuf import struct_pb2
from helloworld import helloworld_pb2, helloworld_pb2_grpc


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHelloBidirectional(self, request_iterator: list[helloworld_pb2.HelloRequest], context: Any) -> AsyncIterator[helloworld_pb2.HelloReply]: # type: ignore
        # 雙向 streaming: 每收到一個 HelloRequest 就回傳一個 HelloReply
        for req in request_iterator:
            msg = f"[雙向] Hello, {req.name}!"
            print(f"Bidirectional received: {req.name}")
            yield helloworld_pb2.HelloReply(message=msg) # type: ignore

    def SayHello(self, request: helloworld_pb2.HelloRequest, context: Any) -> helloworld_pb2.HelloReply: # type: ignore
        return helloworld_pb2.HelloReply(message=f"Hello, {request.name}!") # type: ignore

    def SayHelloManyTimes(self, request: helloworld_pb2.HelloRequest, context: Any) -> helloworld_pb2.HelloReply: # type: ignore
        # Server streaming: 回傳多個 HelloReply
        for i in range(5):
            yield helloworld_pb2.HelloReply(
                message=f"Hello {request.name}, message {i+1}"
            )
            # 模擬延遲
            if i == 4:
                context.abort(grpc.StatusCode.CANCELLED, "Server stopped streaming.")
            time.sleep(1)  # 模擬處理時間

    def SayHelloClientStream(self, request_iterator: list[helloworld_pb2.HelloRequest], context: Any) -> helloworld_pb2.HelloReply: # type: ignore
        # Client streaming: 接收多個 HelloRequest，回傳一個 HelloReply
        names = []
        for req in request_iterator:
            names.append(req.name)
            print(f"Received name: {req.name}")
        joined = ", ".join(names)
        return helloworld_pb2.HelloReply(message=f"Hello to: {joined}") # type: ignore

    def SayHelloWithStruct(self, request: struct_pb2.Struct, context: Any) -> helloworld_pb2.HelloReply: # type: ignore
        # request 為 google.protobuf.Struct
        name = request.fields.get(
            "name", struct_pb2.Value(string_value="匿名")
        ).string_value
        age = request.fields.get("age", struct_pb2.Value(number_value=0)).number_value
        msg = f"Hello, {name}! 你的年齡是 {int(age)}"
        return helloworld_pb2.HelloReply(message=msg) # type: ignore

    def SayComplexHello(self, request: helloworld_pb2.ComplexRequest, context: Any) -> helloworld_pb2.HelloReply: # type: ignore
        # request: ComplexRequest (name, data: Struct)
        name = request.name
        # 取出 data 內所有欄位
        data_fields = []
        for k, v in request.data.fields.items():
            # 根據 value 類型顯示
            if v.WhichOneof("kind") == "string_value":
                data_fields.append(f"{k}: {v.string_value}")
            elif v.WhichOneof("kind") == "number_value":
                data_fields.append(f"{k}: {v.number_value}")
            elif v.WhichOneof("kind") == "bool_value":
                data_fields.append(f"{k}: {v.bool_value}")
            else:
                data_fields.append(f"{k}: (complex type)")
        data_str = "; ".join(data_fields) if data_fields else "無附加資料"
        msg = f"Hello, {name}! 附加資料: {data_str}"
        return helloworld_pb2.HelloReply(message=msg) # type: ignore

    def SayComplexHelloStream(self, request_iterator: list[helloworld_pb2.ComplexRequest], context: Any) -> helloworld_pb2.HelloReply: # type: ignore
        # Client streaming: 收集多個 ComplexRequest，彙整資訊回傳
        names = []
        all_data = []
        for req in request_iterator:
            names.append(req.name)
            data_fields = []
            for k, v in req.data.fields.items():
                if v.WhichOneof("kind") == "string_value":
                    data_fields.append(f"{k}: {v.string_value}")
                elif v.WhichOneof("kind") == "number_value":
                    data_fields.append(f"{k}: {v.number_value}")
                elif v.WhichOneof("kind") == "bool_value":
                    data_fields.append(f"{k}: {v.bool_value}")
                else:
                    data_fields.append(f"{k}: (complex type)")
            all_data.append(
                f"[{req.name}] "
                + ("; ".join(data_fields) if data_fields else "無附加資料")
            )
        msg = f"收到 {len(names)} 筆 ComplexHello：\n" + "\n".join(all_data)
        return helloworld_pb2.HelloReply(message=msg) # type: ignore


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
