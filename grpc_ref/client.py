import grpc
from helloworld import helloworld_pb2, helloworld_pb2_grpc
import time
from google.protobuf import struct_pb2

def run():

    channel = grpc.insecure_channel('localhost:50051')
    stub = helloworld_pb2_grpc.GreeterStub(channel)

    # # # # # # # # # # #
    # 呼叫原本的 SayHello #
    # # # # # # # # # # # 
    response = stub.SayHello(helloworld_pb2.HelloRequest(name='World3333'))
    print("Greeter client received: " + response.message)

    # # # # # # # # # # # # # # # # # # # # # # #
    # 呼叫 Server streaming 的 SayHelloManyTimes #
    # # # # # # # # # # # # # # # # # # # # # # #
    print("Server streaming 範例:")
    responses = stub.SayHelloManyTimes(helloworld_pb2.HelloRequest(name='World'))
    try:
        for resp in responses:
            print("  ", resp.message)
    except grpc.RpcError as e:
        print(f"Stream interrupted: {e.code()} - {e.details()}")

    # # # # # # # # # # # # #
    # Client streaming 範例 #
    # # # # # # # # # # # # #
    print("Client streaming 範例:")
    def request_messages():
        for name in ["Alice", "Bob", "Charlie"]:
            yield helloworld_pb2.HelloRequest(name=name)
            time.sleep(1)
    reply = stub.SayHelloClientStream(request_messages())
    print("  ", reply.message)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # 雙向 streaming 範例
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    print("Bidirectional streaming 範例:")
    def bidi_messages():
        for name in ["Tom", "Jerry", "Spike"]:
            yield helloworld_pb2.HelloRequest(name=name)
            time.sleep(1)
    responses = stub.SayHelloBidirectional(bidi_messages())
    try:
        for resp in responses:
            print("  ", resp.message)
    except grpc.RpcError as e:
        print(f"Bidirectional stream interrupted: {e.code()} - {e.details()}")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Struct 範例
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    print("Struct 範例:")
    s = struct_pb2.Struct()
    s.update({"name": "StructUser", "age": 28})
    response = stub.SayHelloWithStruct(s)
    print("  ", response.message)

if __name__ == '__main__':
    run()