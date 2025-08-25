# Agent Service

This project provides utilities for building multi-agent group chats powered by [AutoGen](https://github.com/microsoft/autogen). The `SelectorGroupChat` class allows conversations to dynamically route messages to the most relevant agent based on configurable selection strategies.

## Installation

```
pip install -r requirements.txt
```

## Usage

The `SelectorGroupChat` class can be used to create a group chat and manage agent selection:

```python
from chat.selector_group_chat import SelectorGroupChat

chat = SelectorGroupChat([...])
chat.start_chat("Hello")
```

## LLM Configuration

The `LLMConfig` helper centralises model settings for all agents. A custom
`base_url` can be supplied via the ``LLM_BASE_URL`` environment variable or by
setting :code:`LLMConfig.base_url` directly. Individual agents may use different
models by populating :code:`LLMConfig.agent_models`:

```python
from config.llm_config import LLMConfig

LLMConfig.base_url = "http://localhost:8000/v1"
LLMConfig.agent_models = {
    "Math_Expert": "gpt-math-8b",
    "Info_Agent": "gpt-info-7b",
}
```

Agents without an explicit entry fall back to ``LLMConfig.default_model``.

## Running

Start the FastAPI application to access the mock subject and chat endpoints:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Alternatively, you can run the entrypoint directly:

```
python main.py
```

The API will be available at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

## Testing

Run type checking and tests:

```
mypy chat/selector_group_chat.py --ignore-missing-imports
pytest
```

