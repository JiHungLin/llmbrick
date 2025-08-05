from typing import AsyncIterator
from llmbrick.bricks.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail, ServiceInfoResponse, ModelInfo
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
    async def get_service_info_method(self) -> ServiceInfoResponse:
        """
        Returns service information for the brick.
        """
        model_info_list = [
            ModelInfo(
                model_id="my_brick_model",
                version="1.0",
                supported_languages=["en", "zh"],
                support_streaming=True,
                description="A model for MyBrick that processes text input and streams output."
            )
        ]
        return ServiceInfoResponse(
            service_name="MyBrickService",
            version="1.0",
            models=model_info_list,
            error=None
        )