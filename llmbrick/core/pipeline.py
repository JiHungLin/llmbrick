from typing import List, Dict, Any
from .brick import BaseBrick
from .event_bus import EventBus

class Pipeline:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.bricks: Dict[str, BaseBrick] = {}
        self.workflow: List[str] = []
    
    def add_brick(self, name: str, brick: BaseBrick) -> 'Pipeline':
        self.bricks[name] = brick
        return self
    
    def set_workflow(self, workflow: List[str]) -> 'Pipeline':
        self.workflow = workflow
        return self
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        current_data = input_data
        for brick_name in self.workflow:
            brick = self.bricks.get(brick_name)
            if brick:
                current_data = await brick.process(current_data)
        return current_data