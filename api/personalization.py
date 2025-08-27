"""Utilities for safely updating agent system messages."""

from typing import List, Callable, Dict, Any

from .agent_base import UpdateSystemMessage, logger


def _get_system_message_text(system_message) -> str:
    if isinstance(system_message, str):
        return system_message
    for attr in ("content", "text", "message", "value"):
        if hasattr(system_message, attr):
            val = getattr(system_message, attr)
            if isinstance(val, str):
                return val
    return str(system_message)


def _set_system_message_text(agent, new_text: str) -> None:
    """Safely update an agent's system message across different implementations."""
    # 1) Official API if available
    if hasattr(agent, "update_system_message"):
        try:
            agent.update_system_message(new_text)
            return
        except TypeError:
            pass
        try:
            try:
                _ = UpdateSystemMessage
            except NameError:
                _ = None
            if _ is not None:
                agent.update_system_message(UpdateSystemMessage(content=new_text))  # type: ignore
                return
        except Exception:
            pass

    # 2) Common internal field
    if hasattr(agent, "_system_message"):
        try:
            agent._system_message = new_text
            return
        except Exception:
            pass

    # 3) Modify in-place if object has 'content'
    sm = getattr(agent, "system_message", None)
    try:
        if hasattr(sm, "content"):
            sm.content = new_text  # type: ignore
            return
    except Exception:
        pass

    # 4) Warn if unable to update
    logger.warning("Could not set system_message on %s; skipping update.", getattr(agent, "name", "agent"))


def make_personalization_updater(agent, context_variables):
    def update_with_context(messages):
        context_data = context_variables.data
        personalization_msg = (
            f"Always respond in {context_data.get('language', 'vi')}. "
            f"Student level: {context_data.get('student_level', 'HS phổ thông')}. "
            f"Curriculum: {context_data.get('curriculum', 'VN K-12')}. "
            f"Goals: {context_data.get('goals', 'Hiểu sâu khái niệm và làm bài tập có hướng dẫn')}"
        )
        current = _get_system_message_text(getattr(agent, "system_message", ""))
        if not current.endswith(personalization_msg):
            new_text = (current + "\n\n" + personalization_msg).strip()
            _set_system_message_text(agent, new_text)
        logger.debug("Ran personalization updater for %s", getattr(agent, "name", "agent"))
    return update_with_context


def chain_updaters(*funcs: Callable[[List[Dict[str, Any]]], None]) -> Callable[[List[Dict[str, Any]]], None]:
    def _runner(messages: List[Dict[str, Any]]) -> None:
        for f in funcs:
            f(messages)
    return _runner

__all__ = [
    "make_personalization_updater",
    "chain_updaters",
]
