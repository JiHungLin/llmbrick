import time

import grpc
from google.protobuf import struct_pb2
from pb2.helloworld import helloworld_pb2, helloworld_pb2_grpc


def run():

    channel = grpc.insecure_channel("localhost:50051")
    stub = helloworld_pb2_grpc.GreeterStub(channel)

    # # # # # # # # # # #
    # 呼叫原本的 SayHello #
    # # # # # # # # # # #
    response = stub.SayHello(helloworld_pb2.HelloRequest(name="World3333"))
    print("Greeter client received: " + response.message)

    # # # # # # # # # # # # # # # # # # # # # # #
    # 呼叫 Server streaming 的 SayHelloManyTimes #
    # # # # # # # # # # # # # # # # # # # # # # #
    print("Server streaming 範例:")
    responses = stub.SayHelloManyTimes(helloworld_pb2.HelloRequest(name="World"))
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # SayComplexHello 範例
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    print("SayComplexHello 範例:")
    complex_data = struct_pb2.Struct()
    complex_data.update({"age": 30, "city": "Taipei", "is_member": True})
    complex_req = helloworld_pb2.ComplexRequest(name="ComplexUser", data=complex_data)
    response = stub.SayComplexHello(complex_req)
    print("  ", response.message)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # SayComplexHelloStream 範例
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    print("SayComplexHelloStream 範例:")

    def complex_stream_messages():
        from google.protobuf import struct_pb2

        datas = [
            {"name": "UserA", "data": {"age": 20, "city": "Taipei"}},
            {
                "name": "UserB",
                "data": {"age": 25, "city": "Kaohsiung", "is_member": True},
            },
            {"name": "UserC", "data": {"age": 30}},
        ]
        for item in datas:
            s = struct_pb2.Struct()
            s.update(item["data"])
            yield helloworld_pb2.ComplexRequest(name=item["name"], data=s)

    reply = stub.SayComplexHelloStream(complex_stream_messages())
    print("  ", reply.message)


if __name__ == "__main__":
    run()
