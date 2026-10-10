"""事件与消息通信总线 (Event & Message Bus)
负责多智能体协同中的异步事件分发、父子 Agent 消息路由与审计追踪。
"""

import time
import logging
from typing import Dict, Any, List, Callable
from pydantic import BaseModel, Field

logger = logging.getLogger("agent_sphere.event_bus")

class AgentMessage(BaseModel):
    message_id: str
    sender: str
    recipient: str  # 可以是指定 Agent 名称或广播 '*'
    topic: str
    payload: Dict[str, Any]
    timestamp: float = Field(default_factory=time.time)

class EventBus:
    """事件消息总线"""
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self.message_history: List[AgentMessage] = []

    def subscribe(self, topic: str, handler: Callable[[AgentMessage], None]):
        """订阅特定主题的事件消息"""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.info(f"订阅主题 [{topic}]")

    def publish(self, sender: str, recipient: str, topic: str, payload: Dict[str, Any]) -> AgentMessage:
        """发布消息并路由至订阅者"""
        msg = AgentMessage(
            message_id=f"msg_{int(time.time()*1000)}_{len(self.message_history)}",
            sender=sender,
            recipient=recipient,
            topic=topic,
            payload=payload
        )
        self.message_history.append(msg)
        logger.info(f"[EventBus] {sender} -> {recipient} on ({topic}): {msg.message_id}")

        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            try:
                handler(msg)
            except Exception as e:
                logger.error(f"事件处理器执行失败 on topic {topic}: {e}", exc_info=True)
        return msg

    def get_messages_for_agent(self, agent_name: str) -> List[AgentMessage]:
        """获取指定 Agent 接收或发送的所有历史消息"""
        return [m for m in self.message_history if m.recipient in [agent_name, "*"] or m.sender == agent_name]
