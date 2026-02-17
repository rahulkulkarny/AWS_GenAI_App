import os
from dotenv import load_dotenv
load_dotenv()
for key, value in os.environ.items():
    print(f"{key}={value}")

from llama_index.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from llama_index.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.llms import ChatMessage, MessageRole

retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.getenv("BEDROCK_KNOWLEDGE_BASE_ID"),
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 3}},
    )
print("retriever:",retriever)

llm = OpenAI(model=os.getenv("OPENAI_MODEL"))

print("llm:",llm)

_knowledge_base_tool = QueryEngineTool.from_defaults(
    query_engine=RetrieverQueryEngine(retriever=retriever),
    name="amazon_knowledge_base",
    description=(
        "A vector database of knowledge about tenancy agreements and related data."
    ),
)

print("_knowledge_base_tool:",_knowledge_base_tool)

agent = ReActAgent(
    tools=[_knowledge_base_tool],
    llm=llm,
    system_prompt=(
        "You are a helpful RAG AI assistant with access to a vector database of knowledge about tenancy agreements."
        "When users ask questions about tenancy agreements, follow these rules:"
        "1) If the context contains a clause that directly answers the question, use that clause."
        "2) If the context contains statements that seem to conflict, you MUST resolve the conflict."
        "3) Do not confuse contractual renewal/extension with statutory security of tenure."
        "4) Include ONE short supporting quote (max 25 words)."
        "5) Keep the answer brief (2–4 sentences)."
        "6) If insufficient, say exactly: 'I do not know based on the provided context.'"
        "7) Use the available tool to retrieve accurate information. "
        "8) Always provide clear and concise answers based on the retrieved information."
        "9) You must use English language for your responses and provide the answer in a concise manner."
    ),
)

print("agent:",agent)


async def get_agent_response(message, chat_history):
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(ChatMessage(role=MessageRole.USER, content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=msg["content"]))

    try:
        nodes = retriever.retrieve(message)
        print("Retriever Nodes Count:", len(nodes))
    except Exception as e:
        return f"AWS/Retriever Error:{type(e).__name__}: {e}"

    if not nodes:
        return "I do not know based on the provided content"

    user_message = ChatMessage(role=MessageRole.USER, content=message)

    response = await agent.run(user_message, chat_history=messages)
    return str(response)

