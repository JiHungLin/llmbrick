import React, { useRef } from 'react';
import Layout from '@theme/Layout';
import { useState } from 'react';

const promptText = `
LLMBrick: Comprehensive Guide to Custom Brick Development and Library Usage

Overview and Purpose
LLMBrick is a modular Python framework designed to solve the challenges of building, composing, and deploying advanced LLM (Large Language Model) applications. It addresses the need for reusable, composable, and maintainable AI components by introducing the concept of “Bricks”—well-defined, pluggable modules that encapsulate specific logic, workflows, or integrations. LLMBrick enables rapid prototyping, scalable deployment, and robust error handling for LLM-powered systems.

Core Features
- Modular Brick system: Each Brick is a self-contained component for tasks like intent detection, text correction, retrieval, translation, or integrating external APIs.
- Standardized protocols: Unified request/response types, error handling, and streaming support (unary, input/output/bidirectional streaming).
- Service deployment: Bricks can be exposed as gRPC or SSE services for distributed or real-time applications.
- Extensibility: Easily create custom Bricks or extend built-in ones.
- Async/await support for high concurrency and non-blocking operations.
- Built-in error codes, logging, and performance monitoring utilities.

Brick System: Base Bricks and Their Interfaces

LLMBrick provides several base Bricks, each designed for a specific NLP or orchestration task. All Bricks inherit from a common interface and expose a set of standard handler functions. Below is an overview of the main base Bricks, their request/response types, and customizable functions:

1. **CommonBrick**
   - Purpose: General-purpose base for custom Bricks.
   - Handlers: 
     - \`run_unary(request: CommonRequest) -> CommonResponse\`
     - \`run_input_streaming(request_stream: AsyncIterable[CommonRequest]) -> CommonResponse\`
     - \`run_output_streaming(request: CommonRequest) -> AsyncIterable[CommonResponse]\`
     - \`run_bidi_streaming(request_stream: AsyncIterable[CommonRequest]) -> AsyncIterable[CommonResponse]\`
     - \`run_get_service_info() -> ServiceInfo\`
   - Request: \`CommonRequest\` (data: dict, metadata: dict)
   - Response: \`CommonResponse\` (data: dict, error: ErrorDetail)
   - Customizable: Override any handler, add custom logic, define new methods.

2. **LLMBrick**
   - Purpose: Integrate and manage LLM (e.g., OpenAI) calls.
   - Handlers:
     - \`run_unary(request: LLMRequest) -> LLMResponse\`
     - \`run_output_streaming(request: LLMRequest) -> AsyncIterable[LLMResponse]\`
   - Request: \`LLMRequest\` (prompt, context, parameters)
   - Response: \`LLMResponse\` (text, tokens, error)
   - Customizable: Model selection, prompt engineering, output formatting.

3. **ComposeBrick**
   - Purpose: Orchestrate multiple Bricks in a pipeline or workflow.
   - Handlers:
     - \`run_unary(request: ComposeRequest) -> ComposeResponse\`
   - Request: \`ComposeRequest\` (steps, data)
   - Response: \`ComposeResponse\` (results, error)
   - Customizable: Define step logic, data flow, error handling between Bricks.

4. **GuardBrick**
   - Purpose: Input validation, filtering, and safety checks.
   - Handlers:
     - \`run_unary(request: GuardRequest) -> GuardResponse\`
   - Request: \`GuardRequest\` (input, rules)
   - Response: \`GuardResponse\` (is_valid, reason, error)
   - Customizable: Validation rules, filtering logic.

5. **IntentionBrick**
   - Purpose: Intent detection and classification.
   - Handlers:
     - \`run_unary(request: IntentionRequest) -> IntentionResponse\`
   - Request: \`IntentionRequest\` (text, context)
   - Response: \`IntentionResponse\` (intent, confidence, error)
   - Customizable: Intent schema, classification logic.

6. **RectifyBrick**
   - Purpose: Text correction and normalization.
   - Handlers:
     - \`run_unary(request: RectifyRequest) -> RectifyResponse\`
   - Request: \`RectifyRequest\` (text, language)
   - Response: \`RectifyResponse\` (corrected_text, error)
   - Customizable: Correction algorithms, language support.

7. **RetrievalBrick**
   - Purpose: Information retrieval from knowledge bases or documents.
   - Handlers:
     - \`run_unary(request: RetrievalRequest) -> RetrievalResponse\`
   - Request: \`RetrievalRequest\` (query, top_k, filters)
   - Response: \`RetrievalResponse\` (documents, scores, error)
   - Customizable: Retrieval backend, ranking logic.

8. **TranslateBrick**
   - Purpose: Multilingual translation.
   - Handlers:
     - \`run_unary(request: TranslateRequest) -> TranslateResponse\`
   - Request: \`TranslateRequest\` (text, source_lang, target_lang)
   - Response: \`TranslateResponse\` (translated_text, error)
   - Customizable: Supported languages, translation engine.

Handler Decorators and Customization
- \`@unary_handler\`: For single request/response logic.
- \`@input_streaming_handler\`: For processing a stream of input requests.
- \`@output_streaming_handler\`: For streaming multiple outputs from a single request.
- \`@bidi_streaming_handler\`: For bidirectional streaming scenarios.
- \`@get_service_info_handler\`: For exposing Brick metadata and capabilities.

All handlers are async and can be overridden to implement custom logic. You can add additional methods or properties as needed.

Request/Response Data Types — Strict Usage Guidelines
**Important:** When developing Bricks, you must use the exact request and response types defined by the framework for each Brick type. Do not invent or substitute your own data structures. For example, a GuardBrick must use \`GuardRequest\` and return \`GuardResponse\`. This ensures compatibility, composability, and correct operation across the LLMBrick ecosystem.

- All Bricks use standardized request/response types, typically with a \`.data\` dictionary for inputs/outputs and an \`error\` field for status.
- Refer to the protocols in \`llmbrick.protocols.models.bricks\` for detailed type definitions.
- Never create custom error fields or codes outside of the provided \`ErrorDetail\` and \`ErrorCodes\` structures.

**Incorrect Example (Do NOT do this):**
\`\`\`python
# ❌ Do NOT define your own request/response or error fields!
class BadBrick(CommonBrick):
    @unary_handler
    async def process(self, request):  # Missing type!
        # Wrong: using custom dict instead of CommonResponse
        return {"result": "bad", "error": "fail"}
\`\`\`

**Correct Example:**
\`\`\`python
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail
from llmbrick.core.error_codes import ErrorCodes

class GoodBrick(CommonBrick):
    @unary_handler
    async def process(self, request: CommonRequest) -> CommonResponse:
        try:
            # Your logic here
            return CommonResponse(
                data={"result": "ok"},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
        except Exception as e:
            return CommonResponse(
                data={},
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message=str(e))
            )
\`\`\`

Extending and Customizing Bricks
- Inherit from any base Brick to add or override handler methods.
- Document the expected input/output schema for your Brick.
- Compose Bricks for complex workflows using ComposeBrick or by chaining outputs/inputs.

Service Deployment and Integration
- Register any Brick as a gRPC or SSE service for distributed or real-time applications.
- Configure service parameters (host, port, etc.) as needed.

Quick Example: Minimal Brick
\`\`\`python
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import unary_handler
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail
from llmbrick.core.error_codes import ErrorCodes

class HelloBrick(CommonBrick):
    @unary_handler
    async def hello(self, request: CommonRequest) -> CommonResponse:
        name = request.data.get("name", "World")
        return CommonResponse(
            data={"message": f"Hello, {name}!"},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
\`\`\`
Test locally:
\`\`\`python
import asyncio
from hello_brick import HelloBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest

async def main():
    brick = HelloBrick()
    req = CommonRequest(data={"name": "Alice"})
    resp = await brick.hello(req)
    print(resp.data["message"])  # Output: Hello, Alice!

if __name__ == "__main__":
    asyncio.run(main())
\`\`\`

Service Deployment Example (gRPC)
\`\`\`python
from llmbrick.servers.grpc.server import GrpcServer
from hello_brick import HelloBrick

brick = HelloBrick()
server = GrpcServer(port=50051)
server.register_service(brick)
server.run()
\`\`\`

Service Deployment Example (SSE)
\`\`\`python
from llmbrick.servers.sse import SSEServer
from hello_brick import HelloBrick

brick = HelloBrick()
server = SSEServer(brick, host="0.0.0.0", port=8000, enable_test_page=True)
server.run()
\`\`\`

Advanced Brick Composition Example
\`\`\`python
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.bricks.llm.base_llm import LLMBrick

guard_brick = GuardBrick()
rectify_brick = RectifyBrick()
intention_brick = IntentionBrick()
llm_brick = LLMBrick()

async def main():
    result1 = await guard_brick.run_unary(guard_request)
    rectify_text = await rectify_brick.run_unary(rectify_request)
    intention_result = await intention_brick.run_unary(rectify_text)
    async for answer in llm_brick.run_output_streaming(question_context):
        print(answer)
\`\`\`

Exception Handling and Using ErrorCodes

LLMBrick provides a robust error handling mechanism using standardized error codes and the \`ErrorDetail\` structure. Each response includes an \`error\` field, which contains a code and message. The \`llmbrick.core.error_codes.ErrorCodes\` module defines common error codes such as \`SUCCESS\`, \`INVALID_INPUT\`, \`NOT_FOUND\`, \`INTERNAL_ERROR\`, etc.

How to Use ErrorCodes in Your Brick:
- Always set the appropriate error code and message in your response.
- Use try/except blocks in your handler methods to catch exceptions and return meaningful error information.
- For custom errors, define your own codes or use the provided ones for consistency.
- Never create your own error code or error field outside of the provided \`ErrorCodes\` and \`ErrorDetail\`.

Example: Error Handling in a Custom Brick
\`\`\`python
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail
from llmbrick.core.error_codes import ErrorCodes

class MyCustomBrick(CommonBrick):
    @unary_handler
    async def process(self, request: CommonRequest) -> CommonResponse:
        try:
            user_input = request.data.get("input", "")
            if not user_input:
                return CommonResponse(
                    data={},
                    error=ErrorDetail(code=ErrorCodes.INVALID_INPUT, message="Input is required")
                )
            # Your logic here
            result = user_input.upper()
            return CommonResponse(
                data={"result": result},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
        except Exception as e:
            return CommonResponse(
                data={},
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message=str(e))
            )
\`\`\`
- Always check the \`error\` field in the response when consuming a Brick’s output.
- Use error codes to implement retry logic, user feedback, or escalation as needed.

[The rest of the previous content remains unchanged, including installation, best practices, and advanced usage.]
# Appendix: All Official Data Structures (Dataclasses & Models)

**You MUST use only the following dataclasses and models for all Brick requests, responses, and data exchange. Do NOT invent or substitute your own data structures.**

## llmbrick.protocols.models.bricks.common_types

- **ErrorDetail**
  - code: int
  - message: str
  - detail: str = ""
- **ModelInfo**
  - model_id: str
  - version: str
  - supported_languages: List[str]
  - support_streaming: bool
  - description: str
- **CommonRequest**
  - data: Dict[str, Any]
- **CommonResponse**
  - data: Dict[str, Any]
  - error: Optional[ErrorDetail]
- **ServiceInfoRequest**
  - (no fields)
- **ServiceInfoResponse**
  - service_name: str
  - version: str
  - models: List[ModelInfo]
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.compose_types

- **Document**
  - doc_id: str
  - title: str
  - snippet: str
  - score: float
  - metadata: Dict[str, Any]
- **ComposeRequest**
  - input_documents: List[Document]
  - target_format: str
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
- **ComposeResponse**
  - output: Dict[str, Any]
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.guard_types

- **GuardRequest**
  - text: str
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
- **GuardResult**
  - is_attack: bool
  - confidence: float
  - detail: str
- **GuardResponse**
  - results: List[GuardResult]
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.intention_types

- **IntentionRequest**
  - text: str
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
- **IntentionResult**
  - intent_category: str
  - confidence: float
- **IntentionResponse**
  - results: List[IntentionResult]
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.llm_types

- **Context**
  - role: str
  - content: str
- **LLMRequest**
  - temperature: float
  - model_id: str
  - prompt: str
  - context: List[Context]
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
  - max_tokens: int
- **LLMResponse**
  - text: str
  - tokens: List[str]
  - is_final: bool
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.rectify_types

- **RectifyRequest**
  - text: str
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
- **RectifyResponse**
  - corrected_text: str
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.retrieval_types

- **RetrievalRequest**
  - query: str
  - max_results: int
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
- **Document**
  - doc_id: str
  - title: str
  - snippet: str
  - score: float
  - metadata: Dict[str, Any]
- **RetrievalResponse**
  - documents: List[Document]
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.bricks.translate_types

- **TranslateRequest**
  - text: str
  - model_id: str
  - target_language: str
  - client_id: str
  - session_id: str
  - request_id: str
  - source_language: str
- **TranslateResponse**
  - text: str
  - tokens: List[str]
  - language_code: str
  - is_final: bool
  - error: Optional[ErrorDetail]

## llmbrick.protocols.models.http.conversation

- **Message** (Pydantic model)
  - role: str
  - content: str
- **ConversationSSERequest** (Pydantic model)
  - model: str
  - messages: List[Message]
  - stream: bool
  - client_id: Optional[str]
  - session_id: str
  - temperature: Optional[float]
  - max_tokens: Optional[int]
  - tools: Optional[List[Any]]
  - tool_choice: Optional[Any]
  - source_language: Optional[str]
- **SSEContext** (Pydantic model)
  - conversation_id: Optional[str]
  - cursor: Optional[str]
- **SSEResponseMetadata** (Pydantic model)
  - search_results: Optional[Any]
  - attachments: Optional[Any]
- **ConversationSSEResponse** (Pydantic model)
  - id: str
  - type: str
  - model: Optional[str]
  - text: Optional[str]
  - progress: str
  - context: Optional[SSEContext]
  - metadata: Optional[SSEResponseMetadata]

**Always refer to these official dataclasses and models for all Brick and API development. Do NOT create or use custom request/response or error types.**
`;

export default function PromptPage() {
  const preRef = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (preRef.current) {
      navigator.clipboard.writeText(promptText);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  return (
    <Layout title="LLMBrick Prompt">
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1rem' }}>
        <h1>LLMBrick Prompt</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
          <button
            onClick={handleCopy}
            style={{
              padding: '0.5rem 1.2rem',
              fontSize: '1rem',
              cursor: 'pointer',
              background: '#3578e5',
              color: 'white',
              border: 'none',
              borderRadius: 4,
            }}
          >
            一鍵複製
          </button>
          {copied && (
            <span style={{ color: '#3578e5', fontWeight: 600, fontSize: '1rem' }}>
              已複製!
            </span>
          )}
        </div>
        <pre
          ref={preRef}
          style={{
            background: '#222',
            color: '#fff',
            padding: '1.5rem',
            borderRadius: 8,
            overflowX: 'auto',
            fontSize: '0.95rem',
            lineHeight: 1.5,
            maxHeight: 600,
          }}
        >
          {promptText}
        </pre>
      </div>
    </Layout>
  );
}