import pytest
from llmbrick.core import brick

class MyBrick(brick.BaseBrick):
    allowed_handler_types = {"unary", "get_service_info"}

    @brick.unary_handler
    async def my_unary(self, x):
        return x + 1

    @brick.get_service_info_handler
    async def my_info(self):
        return {"service_name": "MyBrick", "version": "test", "models": []}

def test_handler_registration():
    b = MyBrick()
    assert b._unary_handler is not None
    assert b._get_service_info_handler is not None

@pytest.mark.asyncio
async def test_run_unary_success():
    b = MyBrick()
    result = await b.run_unary(2)
    assert result == 3

@pytest.mark.asyncio
async def test_run_unary_not_implemented():
    class NoUnary(brick.BaseBrick):
        pass
    b = NoUnary()
    with pytest.raises(NotImplementedError):
        await b.run_unary(1)

@pytest.mark.asyncio
async def test_run_get_service_info():
    b = MyBrick()
    info = await b.run_get_service_info()
    assert info["service_name"] == "MyBrick"
    assert info["version"] == "test"