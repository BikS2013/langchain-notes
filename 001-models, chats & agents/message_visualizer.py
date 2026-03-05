from typing import Union, List, Dict
from pprint import pprint
from langchain_core.messages import BaseMessage

def message_to_dict(message: Union[BaseMessage, tuple]) -> Dict:
    """Convert a ChatMessage object or tuple to a dictionary with all attributes.
    
    Args:
        message: The message object or tuple to convert
        
    Returns:
        Dictionary containing message content and metadata
    """
    if isinstance(message, tuple):
        if len(message) == 2 and isinstance(message[1], BaseMessage):
            message = message[1]
        else:
            raise ValueError("Invalid tuple format. Expected (role, BaseMessage)")
            
    result = {
        "content": message.content,
        "type": type(message).__name__,
        "additional_kwargs": message.additional_kwargs,
        "id": getattr(message, "id", None),
        "response_metadata": getattr(message, "response_metadata", {}),
        "usage_metadata": getattr(message, "usage_metadata", {}),
        "example": getattr(message, "example", False)
    }
    
    # Add AIMessage specific fields
    if hasattr(message, "tool_calls"):
        result["tool_calls"] = getattr(message, "tool_calls", [])
        result["tool_call_id"] = getattr(message, "tool_call_id", None)
        
    return result

def visualize_messages(result: Union[BaseMessage, List[BaseMessage], tuple]) -> Union[Dict, List[Dict]]:
    """Convert single message, message list, or message tuple to dictionary format.
    
    Args:
        result: Either a single message, list of messages, or tuple of messages
        
    Returns:
        Dictionary or list of dictionaries representing the messages
    """
    if isinstance(result, list):
        return [message_to_dict(msg) for msg in result]
    elif isinstance(result, tuple):
        return message_to_dict(result)
    return message_to_dict(result)

def print_messages(result: Union[BaseMessage, List[BaseMessage]]) -> None:
    """Pretty print the structure of message(s).
    
    Args:
        result: Either a single message or list of messages
    """
    pprint(visualize_messages(result))

# Example usage
if __name__ == "__main__":
    # Test with a single message
    from langchain_core.messages import AIMessage
    msg = AIMessage(content="Hello!")
    print_messages(msg)
    
    # Test with multiple messages
    from langchain_core.messages import SystemMessage, HumanMessage
    messages = [
        SystemMessage(content="You are helpful"),
        HumanMessage(content="Hi"),
        AIMessage(content="Hello!")
    ]
    print_messages(messages)
