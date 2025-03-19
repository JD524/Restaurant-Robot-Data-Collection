# Run the code, and enter your question when prompted with "Enter your question: "
# The code will then ouput the responses from each of the AI Chatbots being used
# I commented out some of the chatbots because they required money to use, but you can uncomment those lines if have an API Key that is usable

import getpass
import os
import asyncio
from langchain.chat_models import init_chat_model
# from databricks_langchain import ChatDatabricks
from langchain.schema import HumanMessage

# --------------------------
API_KEYS = {
    "OPENAI_API_KEY": "",
    "ANTHROPIC_API_KEY": "",
    "COHERE_API_KEY": "",
    "FIREWORKS_API_KEY": "",
    "MISTRAL_API_KEY": "",
    "TOGETHER_API_KEY": "",
    "DATABRICKS_TOKEN": "",
    "GROQ_API_KEY": "",
}

# Set each API key into the environment
for key, value in API_KEYS.items():
    os.environ[key] = value
# --------------------------

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = getpass.getpass("Enter API key for Anthropic: ")

if not os.environ.get("COHERE_API_KEY"):
    os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")

if not os.environ.get("FIREWORKS_API_KEY"):
    os.environ["FIREWORKS_API_KEY"] = getpass.getpass("Enter API key for Fireworks AI: ")

if not os.environ.get("MISTRAL_API_KEY"):
    os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")

if not os.environ.get("TOGETHER_API_KEY"):
    os.environ["TOGETHER_API_KEY"] = getpass.getpass("Enter API key for Together AI: ")

if not os.environ.get("DATABRICKS_TOKEN"):
    os.environ["DATABRICKS_TOKEN"] = getpass.getpass("Enter API key for Databricks: ")

if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

# For Databricks, set the host (update the URL with your actual workspace endpoint)
# if not os.environ.get("DATABRICKS_HOST"):
#     os.environ["DATABRICKS_HOST"] = "https://example.staging.cloud.databricks.com/serving-endpoints"

# --------------------------
# Initialize Chat Models
# --------------------------
# openai_model = init_chat_model("gpt-4o-mini", model_provider="openai")
# anthropic_model = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")
cohere_model = init_chat_model("command-r-plus", model_provider="cohere")
# fireworks_model = init_chat_model("accounts/fireworks/models/llama-v3p1-70b-instruct", model_provider="fireworks")
mistralai_model = init_chat_model("mistral-large-latest", model_provider="mistralai")
together_model = init_chat_model("mistralai/Mixtral-8x7B-Instruct-v0.1", model_provider="together")
# databricks_model = ChatDatabricks(endpoint="databricks-meta-llama-3-1-70b-instruct")
groq_model = init_chat_model("llama3-8b-8192", model_provider="groq")


# --------------------------
# Helper function to query a model asynchronously
# --------------------------
async def query_model(name: str, model, question: str) -> dict:
    messages = [HumanMessage(content=question)]
    response = await asyncio.to_thread(model.invoke, messages)
    return {name: response.content}


# --------------------------
# Summarization function using the OpenAI model as the summarizer
# --------------------------
async def summarize_responses(responses: dict) -> str:
    combined_text = "\n".join([f"{name}: {content}" for name, content in responses.items()])
    summary_prompt = f"Summarize the key points of the following responses:\n\n{combined_text}"
    messages = [HumanMessage(content=summary_prompt)]
    summary_response = await asyncio.to_thread(mistralai_model.invoke, messages)
    return summary_response.content


# --------------------------
# Main asynchronous function
# --------------------------
async def main():
    question = input("Enter your question: ")

    # Create tasks for each model
    tasks = [
        # query_model("OpenAI", openai_model, question),
        # query_model("Anthropic", anthropic_model, question),
        query_model("Cohere", cohere_model, question),
        # query_model("Fireworks AI", fireworks_model, question),
        query_model("Mistral AI", mistralai_model, question),
        query_model("Together AI", together_model, question),
        # query_model("Databricks", databricks_model, question),
        query_model("Groq", groq_model, question),
    ]

    responses_list = await asyncio.gather(*tasks)
    responses = {name: content for response in responses_list for name, content in response.items()}

    # Print individual responses
    for name, content in responses.items():
        print(f"\n{name}:\n{content}\n")

    # Generate and print summary
    summary = await summarize_responses(responses)
    print("\n=== Summary of Responses ===\n")
    print(summary)


if __name__ == "__main__":
    asyncio.run(main())
