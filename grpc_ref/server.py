import grpc
from concurrent import futures
from helloworld import helloworld_pb2, helloworld_pb2_grpc
import time
from google.protobuf import struct_pb2

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHelloBidirectional(self, request_iterator, context):
        # 雙向 streaming: 每收到一個 HelloRequest 就回傳一個 HelloReply
        for req in request_iterator:
            msg = f"[雙向] Hello, {req.name}!"
            print(f"Bidirectional received: {req.name}")
            yield helloworld_pb2.HelloReply(message=msg)

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message=f'Hello, {request.name}!')

    def SayHelloManyTimes(self, request, context):
        # Server streaming: 回傳多個 HelloReply
        for i in range(5):
            yield helloworld_pb2.HelloReply(message=f'Hello {request.name}, message {i+1}')
            # 模擬延遲
            if i == 4:
                context.abort(grpc.StatusCode.CANCELLED, "Server stopped streaming.")
            time.sleep(1)  # 模擬處理時間

    def SayHelloClientStream(self, request_iterator, context):
        # Client streaming: 接收多個 HelloRequest，回傳一個 HelloReply
        names = []
        for req in request_iterator:
            names.append(req.name)
            print(f"Received name: {req.name}")
        joined = ', '.join(names)
        return helloworld_pb2.HelloReply(message=f'Hello to: {joined}')

    def SayHelloWithStruct(self, request, context):
        # request 為 google.protobuf.Struct
        name = request.fields.get("name", struct_pb2.Value(string_value="匿名")).string_value
        age = request.fields.get("age", struct_pb2.Value(number_value=0)).number_value
        msg = f"Hello, {name}! 你的年齡是 {int(age)}"
        return helloworld_pb2.HelloReply(message=msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()