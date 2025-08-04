from typing import AsyncIterator
from llmbrick.bricks.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import ( 
    unary_handler, 
    input_streaming_handler, 
    output_streaming_handler, 
    bidi_streaming_handler,
    get_service_info_handler
)

class MyBrick(CommonBrick):
    """
    MyBrick is a custom brick that extends the CommonBrick functionality.
    It can be used to define specific behaviors or properties for a brick in the LLMBrick framework.
    """

    def __init__(self, my_init_data: str = "", res_prefix: str = "my_brick", **kwargs):
        super().__init__(**kwargs)
        self.my_init_data = my_init_data
        self.res_prefix = res_prefix

    @unary_handler
    async def unary_method(self, input_data: CommonRequest) -> CommonResponse:
        """
        A unary method that processes input data and returns a string.
        """
        
        output = input_data.data.get("text", "")
        if not output:
            error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            response = CommonResponse(error=error)
        else:
            response = CommonResponse(data={"text": output})
        return response

    @input_streaming_handler
    async def input_streaming_method(self, input_stream: AsyncIterator[CommonRequest]) -> CommonResponse:
        """
        An input streaming method that processes a stream of input data.
        """
        has_empty_input = False
        input_data_list = []
        async for input_data in input_stream:
            text = input_data.data.get("text", "")
            if not text:
                has_empty_input = True
            input_data_list.append(text)
        if has_empty_input:
            error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            return CommonResponse(error=error)

        output = "Processed input stream with {} items. Full text: {}".format(len(input_data_list), " ".join(input_data_list))
        return CommonResponse(data={"text": output})
    
    @output_streaming_handler
    async def output_streaming_method(self, input_data: CommonRequest) -> AsyncIterator[CommonResponse]:
        """
        An output streaming method that yields responses based on input data.
        """
        text = input_data.data.get("text", "")
        if not text:
            error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            yield CommonResponse(error=error)
            return
        
        for i in range(5):  # Simulating a streaming response
            yield CommonResponse(data={"text": f"{text} - part {i + 1}"})

    @bidi_streaming_handler
    async def bidi_streaming_method(self, stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]:
        """
        A bidirectional streaming method that processes a stream of requests and yields responses.
        """
        async for input_data in stream:
            text = input_data.data.get("text", "")
            if not text:
                error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
                yield CommonResponse(error=error)
                continue
            
            # Simulating processing and yielding a response
            yield CommonResponse(data={"text": f"Received: {text}"})

    @get_service_info_handler
    def get_service_info_method(self):
        """
        Returns service information for the brick.
        """
        return {
            "name": self.res_prefix,
            "description": "My custom brick for demonstration purposes.",
            "version": "1.0.0"
        }
    

if __name__ == "__main__":
    # Example usage of MyBrick
    my_brick = MyBrick(my_init_data="Initialization data")
    import asyncio

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            service_info = my_brick.run_get_service_info()
            print(service_info)

        asyncio.run(example())

    run_get_service_info_example()

    print("\n\n=== Unary Method ===")
    # Example of running a unary method
    def run_unary_example(is_test_error=False):
        
        async def example():
            request = CommonRequest(data={"text": "Hello, World!"})
            if is_test_error:
                request.data["text"] = ""  # Trigger error
            response = await my_brick.run_unary(request)
            print(response)

        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_unary_example(is_test_error=True)

    print("\n\n=== Input Streaming Method ===")
    # Example of running an input streaming method
    def run_input_streaming_example(is_test_error=False):
        async def example():
            async def input_stream():
                for i in range(3):
                    yield CommonRequest(data={"text": f"Input {i + 1}"})
                yield CommonRequest(data={})  # Simulating an empty input

            response = await my_brick.run_input_streaming(input_stream())
            print(response)

        asyncio.run(example())

    print("Normal case:")
    run_input_streaming_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_input_streaming_example(is_test_error=True)

    print("\n\n=== Output Streaming Method ===")
    # Example of running an output streaming method
    def run_output_streaming_example(is_test_error=False):
        async def example():
            request = CommonRequest(data={"text": "Streaming output"})
            if is_test_error:
                request.data["text"] = ""
            async for response in my_brick.run_output_streaming(request):
                print(response)

        asyncio.run(example())

    print("Normal case:")
    run_output_streaming_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_output_streaming_example(is_test_error=True)


    print("\n\n=== Bidirectional Streaming Method ===")
    # Example of running a bidirectional streaming method
    def run_bidi_streaming_example(is_test_error=False):
        async def example():
            async def bidi_input_stream():
                for i in range(3):
                    yield CommonRequest(data={"text": f"Bidirectional input {i + 1}"})
                yield CommonRequest(data={})

            async for response in my_brick.run_bidi_streaming(bidi_input_stream()):
                print(response)

        asyncio.run(example())

    print("Normal case:")
    run_bidi_streaming_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_bidi_streaming_example(is_test_error=True)
