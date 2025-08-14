from langchain_google_genai import ChatGoogleGenerativeAI

def get_default_model():
    return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.65)

def get_fast_model():
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.7)

def get_local_model():
    from lmstudio import ChatLMStudio
    return ChatLMStudio(model="qwen_qwq-32b", temperature=0.7, format="json")

