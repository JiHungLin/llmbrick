"""
OpenAI GPT Brick implementation for LLMBrick framework.
"""
import os
from typing import AsyncGenerator, List, Optional, Union

from openai import AsyncOpenAI
from llmbrick.utils.logging import log_function, logger
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, Context
from llmbrick.core.error_codes import ErrorCodes

class OpenAIGPTBrick(LLMBrick):
    """OpenAI GPT implementation of LLMBrick.
    
    Attributes:
        default_prompt (str): Default prompt to use if none provided.
        model_id (str): OpenAI model ID to use (e.g. "gpt-3.5-turbo", "gpt-4", "gpt-4o").
        client (AsyncOpenAI): Async OpenAI client instance.
        supported_models (List[str]): List of supported OpenAI model IDs.
    """
    
    def __init__(self, 
                 default_prompt: str = "",
                 model_id: str = "gpt-3.5-turbo",
                 api_key: Optional[str] = None,
                 **kwargs):
        """Initialize OpenAI GPT Brick.
        
        Args:
            default_prompt (str, optional): Default prompt to use. Defaults to "".
            model_id (str, optional): OpenAI model ID ("gpt-3.5-turbo", "gpt-4", "gpt-4o"). Defaults to "gpt-3.5-turbo".
            api_key (Optional[str], optional): OpenAI API key. Defaults to None.
                If not provided, will try to get from OPENAI_API_KEY environment variable.
        """
        super().__init__(default_prompt=default_prompt, **kwargs)
        
        self.model_id = model_id
        self.supported_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        
        # Get API key from argument or environment variable
        # Get API key and initialize client
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found in environment or constructor")
            raise ValueError(
                "OpenAI API key must be provided either through constructor "
                "or OPENAI_API_KEY environment variable"
            )
        
        # Initialize async OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info(f"OpenAIGPTBrick initialized with model {model_id}")

    @log_function(service_name="OpenAIGPTBrick", level="debug")
    async def _create_chat_completion(
        self,
        request: LLMRequest,
        stream: bool = False
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Create a chat completion using OpenAI API.
        
        Args:
            request (LLMRequest): The LLM request containing prompt and parameters.
            stream (bool, optional): Whether to stream the response. Defaults to False.
            
        Returns:
            Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
                Either a complete response or streaming response chunks.
        """
        # Convert context list to OpenAI messages format
        messages = []
        for ctx in request.context:
            messages.append({
                "role": ctx.role or "user",
                "content": ctx.content
            })
        
        # Add the main prompt as the final user message
        messages.append({
            "role": "user",
            "content": request.prompt or self.default_prompt
        })
        
        # Call OpenAI API
        return await self.client.chat.completions.create(
            model=request.model_id or self.model_id,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens if request.max_tokens > 0 else None,
            stream=stream
        )

    @unary_handler
    @log_function(service_name="OpenAIGPTBrick", level="info")
    async def unary_method(self, request: LLMRequest) -> LLMResponse:
        """Handle a single request-response interaction.
        
        Args:
            request (LLMRequest): The request containing prompt and parameters.
            
        Returns:
            LLMResponse: The generated response.
        """
        try:
            completion = await self._create_chat_completion(request, stream=False)
            return LLMResponse(
                text=completion.choices[0].message.content,
                tokens=[],  # OpenAI doesn't provide token-by-token breakdown
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
        except Exception as e:
            return LLMResponse(
                text="",
                tokens=[],
                is_final=True,
                error=ErrorDetail(code=1, message=str(e))
            )

    @output_streaming_handler
    @log_function(service_name="OpenAIGPTBrick", level="info")
    async def output_streaming_method(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:
        """Handle a streaming response interaction.
        
        Args:
            request (LLMRequest): The request containing prompt and parameters.
            
        Yields:
            LLMResponse: Generated response chunks.
        """
        try:
            async for chunk in await self._create_chat_completion(request, stream=True):
                if not chunk.choices[0].delta.content:
                    continue
                    
                yield LLMResponse(
                    text=chunk.choices[0].delta.content,
                    tokens=[],  # OpenAI doesn't provide token-by-token breakdown
                    is_final=False,
                    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
                )
                
            # Send final chunk
            yield LLMResponse(
                text="",
                tokens=[],
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
            
        except Exception as e:
            yield LLMResponse(
                text="",
                tokens=[],
                is_final=True,
                error=ErrorDetail(code=1, message=str(e))
            )

    @get_service_info_handler
    @log_function(service_name="OpenAIGPTBrick", level="info")
    async def get_service_info_method(self) -> ServiceInfoResponse:
        """Get information about this service.
        
        Returns:
            ServiceInfoResponse: Service metadata including supported models.
        """
        return ServiceInfoResponse(
            service_name="OpenAI GPT Brick",
            version="1.0.0",
            models=self.supported_models,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )