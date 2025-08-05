# 教學導覽 Tutorials

本區收錄 llmbrick 的實戰教學，帶你從零打造專屬 AI 服務。

```{toctree}
:maxdepth: 1
:caption: 教學主題

brick_developer_guide
first_llmbrick
```

---

## 打造你的第一個 LLMBrick

### 步驟 1：建立專案與安裝

```bash
pip install llmbrick
```

### 步驟 2：撰寫 LLMBrick

```python
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import unary_handler
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, ErrorDetail

class MyLLM(LLMBrick):
    @unary_handler
    async def reply(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=f"你說了：{request.prompt}",
            tokens=["你", "說", "了"],
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

### 步驟 3：執行與測試

```python
import asyncio

async def main():
    brick = MyLLM()
    req = LLMRequest(prompt="Hello llmbrick!", context=[])
    resp = await brick.run_unary(req)
    print(resp.text)  # 輸出: 你說了：Hello llmbrick!

asyncio.run(main())
```

---

## 更多教學

- 進階開發請參考 [brick_developer_guide](brick_developer_guide.md)
- 歡迎貢獻你的教學案例！