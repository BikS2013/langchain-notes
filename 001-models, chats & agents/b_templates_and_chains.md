# Understanding LangChain Templates, Chains, and Runnables

This document explores key LangChain concepts demonstrated in the accompanying code sample. We'll examine how LangChain facilitates the composition of complex operations with language models through templates, chains, and runnables.

> For a comprehensive overview of LangChain's architecture and concepts, visit the [Conceptual Guide](https://python.langchain.com/docs/concepts/)

## Library Imports and Their Roles

[Learn more about LangChain's architecture](https://python.langchain.com/docs/concepts/architecture)

The example begins with several important imports that provide the foundation for working with LangChain:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
```
These imports provide interfaces to different LLM providers, allowing you to work with various models (OpenAI, Anthropic, Google) using a consistent interface.

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
```
These classes represent different types of messages in a conversation, enabling structured communication with the LLM.

```python
from langchain.prompts import ChatPromptTemplate
```
This import provides the templating functionality for creating reusable prompt patterns.

```python
from langchain.schema.runnable import RunnableLambda
```
This enables creation of custom runnable components that can be integrated into chains.

## The 'invoke' Pattern

Throughout LangChain, the `invoke` method is used consistently across different components to execute operations. This consistent pattern makes the code more predictable and easier to understand:

1. **Template Invocation**:
```python
prompt = prompt_template.invoke({ "x": 12 })
```
Here, `invoke` applies the template with specific variables.

2. **Model Invocation**:
```python
result = model.invoke(prompt)
```
The same `invoke` method is used to send prompts to the language model.

3. **Chain Invocation**:
```python
result = chain.invoke({ "x": 12 })
```
Chains also use `invoke`, maintaining consistency even when working with composed operations.

This consistent use of `invoke` across different components is a key design pattern in LangChain, making it easier to:
- Understand how to execute different components
- Compose complex operations
- Maintain consistent error handling
- Create predictable interfaces

[Learn more about using invoke](https://python.langchain.com/docs/expression_language/interface)


## Prompt Templates

Prompt templates are reusable patterns for generating prompts. LangChain provides the `ChatPromptTemplate` class to create structured prompts that can be parameterized and reused.

### Basic Template Usage

```python
template = "calculate the square of {x}"
prompt_template = ChatPromptTemplate.from_template(template)
prompt = prompt_template.invoke({ "x": 12 })
```

In this example, we create a simple template with a placeholder `{x}`. The `from_template` method creates a `ChatPromptTemplate` that can be invoked with specific values.


### Structured Messages Template

LangChain also supports creating templates from structured messages using tuples:

```python
messages_template = [
    ("system", """You are a system capable of calculating arithmetic expressions.
            You must answer any question returning the result and a detailed explanation of the approach you followed to find it."""),
    ("human", "calculate the square of {x}"),
]

prompt_template = ChatPromptTemplate.from_messages(messages_template)
```

Important: The use of tuples `(role, content)` in the messages_template list is required for the templating to work correctly. Each tuple must contain:
- First element: the role ("system" or "human")
- Second element: the actual message content

This tuple-based structure is not just for clarity - it's a requirement. The `from_messages` method specifically expects this format to properly create templated messages. If you don't use tuples, the message templating will fail. The method uses this structure to create appropriate SystemMessage and HumanMessage objects internally while maintaining the ability to template the content.


This approach allows you to define both system and user messages, providing more control over the conversation structure while maintaining clear role distinctions through the tuple format.


## Chains

Chains are a fundamental concept in LangChain that allow you to combine multiple components into a single pipeline. The pipe operator (`|`) is used to create chains, making it easy to compose operations. This is a key feature of LangChain's Expression Language (LCEL).


### Basic Chain

```python
chain = prompt_template | model
result = chain.invoke({"x": 12})
```

This creates a simple chain that:
1. Takes the input and applies the prompt template
2. Sends the resulting prompt to the model
3. Returns the model's response


## Runnables

Runnables are components that can process inputs and produce outputs. They are the building blocks of chains and can be combined using the pipe operator.

### RunnableLambda

The `RunnableLambda` class allows you to create custom runnable components from Python functions:

```python
print_content = RunnableLambda(lambda x: (
    print(x.content),
    x
))

chain = prompt_template | model | print_content
```

This example creates a runnable that:
1. Prints the content of the message
2. Returns the original message (allowing it to be used in chains)

[Learn more about Runnables](https://python.langchain.com/docs/expression_language/interface)

## Model Integration

The code demonstrates integration with various LLM providers:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
```

LangChain provides consistent interfaces for different language models, making it easy to switch between providers while maintaining the same workflow structure.

[Learn more about LLM Integration](https://python.langchain.com/docs/integrations/llms/)

## Key Benefits

1. **Modularity**: Components can be easily combined and reused
2. **Flexibility**: Support for different LLM providers with consistent interfaces
3. **Composability**: Simple syntax for creating complex pipelines
4. **Extensibility**: Custom components can be created using RunnableLambda

These concepts form the foundation for building more complex applications with LangChain, such as agents, question-answering systems, and conversational interfaces.