from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .config import Config

class BaseBrick(ABC):
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "service": self.name}