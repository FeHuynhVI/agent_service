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

