# API 參考

本區提供 llmbrick 主要類別與方法的 API 參考，協助你快速查詢各元件的用法與介面。

```{toctree}
:maxdepth: 1
:caption: API 模組

common_brick
llm_brick
compose_brick
guard_brick
intention_brick
rectify_brick
retrieval_brick
translate_brick
```

---

## CommonBrick 主要 API

### 類別

- `CommonBrick`
    - 統一異步處理介面，支援本地與 gRPC 調用。

### 常用方法

- `run_unary(request: CommonRequest) -> CommonResponse`
- `run_output_streaming(request: CommonRequest) -> AsyncIterator[CommonResponse]`
- `run_input_streaming(request_stream: AsyncIterator[CommonRequest]) -> CommonResponse`
- `run_bidi_streaming(request_stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]`
- `run_get_service_info() -> ServiceInfoResponse`

### 範例

```python
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest

brick = CommonBrick()
req = CommonRequest(data={"foo": "bar"})
resp = await brick.run_unary(req)
print(resp.data)
```

---

## 更多 API

- 其他 Brick（如 LLMBrick、ComposeBrick 等）請參考對應指南或後續 API 文件。
- 歡迎貢獻更多 API 文件，詳見 [GitHub](https://github.com/JiHungLin/llmbrick)。