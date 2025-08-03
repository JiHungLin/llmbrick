# Release v0.2.3: Enhanced Error Handling and System Reliability

This release focuses on improving system reliability through enhanced error handling, particularly in gRPC wrappers, along with various documentation improvements and bug fixes.

## Major Changes
- Refactored gRPC wrappers across all brick types to improve error handling and response validation
- Enhanced SSE server request validation and error handling
- Improved type hints and error handling in OpenAI LLM brick

## Bug Fixes
- Fixed chat completions request body validation in SSE server
- Updated type hints in OpenAI LLM brick for better clarity
- Improved error handling and mock setup in OpenAI GPT Brick tests

## Documentation
- Reorganized guide entries for better clarity and accessibility
- Updated README with corrected documentation links
- Added missing badges and improved link accessibility
- Fixed various documentation links for better user experience

## Cleanup
- Removed development notebook and script files
- Streamlined error handling across all gRPC wrapper implementations