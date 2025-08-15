import os
import json
import base64
import asyncio
import logging
import httpx
from fastapi import FastAPI, WebSocket, Request, Form, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv
from langgraph import create_graph, Node
from langgraph.prebuilt import create_react_agent
from langgraph.func import entrypoint
from langgraph.store.memory import InMemoryStore
from langmem import create_memory_store_manager, create_manage_memory_tool, create_search_memory_tool
from copilotkit import HandlerBuilder
from google.generativeai import Client as GeminiClient
from ..tools.tts import text_to_audio_stream, AsyncGenerator

from prompt import DEFAULT_SYSTEM_PROMPT, SMS_SYSTEM_PROMPT

# ENV CONFIG
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
VOICE_ID = os.getenv("VOICE_ID")
WHISPER_API_URL = os.getenv("WHISPER_API_URL", "http://localhost:9000/asr")

if not all([ELEVENLABS_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, VOICE_ID]):
    raise ValueError("Missing required environment variables.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
gemini = GeminiClient() # No model specified here, it will be in the chat call
gem = "google:gemini-2.5-flash-latest"
gemi = "google:gemini-2.5-pro-latest"

# MEMORY SETUP
store = InMemoryStore(index={"dims": 768, "embed": "google:text-embedding-004"}) 

memory_manager = create_memory_store_manager(
    model=gemi,
    namespace=("semantic", "episodes"),
    schemas=None,
    instructions=(
        "For semantic memory store facts and relationships. "
        "For episodic store noteworthy problem-solving examples."
    ),
    enable_inserts=True,
)

memory_review_agent = create_react_agent(
    model=gemi,
    prompt=lambda state: [{
        "role": "system",
        "content": (
            "You are a memory curator. Review and prune or update semantic memories, "
            "and consolidate episodic entries if needed. Tools: manage, search."
        )
    }, *state["messages"]],
    tools=[
        create_manage_memory_tool(namespace=("semantic",)),
        create_search_memory_tool(namespace=("semantic",)),
        create_manage_memory_tool(namespace=("episodes",)),
        create_search_memory_tool(namespace=("episodes",)),
    ]
)

# LANGGRAPH WORKFLOW
graph = create_graph()

async def transcribe_audio(audio_payload: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(WHISPER_API_URL, data={"audio": audio_payload})
        resp.raise_for_status()
        return resp.json().get("text", "")

transcribe_node = Node("transcribe", func=transcribe_audio, inputs=["audio_payload"], outputs=["transcription"])
graph.add_node(transcribe_node)

async def generate_gemini_response(transcription: str, system_prompt: str, instructions: str, context: str):
    session_messages = await memory_manager.load_history(transcription)
    
    # Construct the final prompt to be sent to the LLM
    final_system_prompt = system_prompt.format(
        INSTRUCTIONS=instructions,
        CONTEXT=context,
        USER_MESSAGE=transcription
    )
    
    msgs = [{"role": "system", "content": final_system_prompt}]
    for m in session_messages:
        msgs.append({"role": m["role"], "content": m["content"]})
    
   

    stream = gemini.chat.stream(model=gem, messages=msgs, temperature=0.7)
    full = ""
    async for chunk in stream:
        text = getattr(chunk, "text", "")
        full += text
        yield text
    
    await memory_manager.append({"role": "assistant", "content": full})
    # Trigger memory review non-blockingly
    asyncio.create_task(memory_review_agent.invoke({"messages": msgs + [{"role": "assistant", "content": full}]}))


generate_node = Node(
    "generate",
    func=generate_gemini_response,
    inputs=["transcription", "system_prompt", "instructions", "context"],
    outputs=["response_chunk"],
)
graph.add_node(generate_node)
graph.add_edge("transcribe", "generate")

async def twilio_tts_handler(
    response_chunk_stream: AsyncGenerator[str, None],
    websocket: WebSocket,
    stream_sid: str
):
    """
    A specific handler for the Twilio use case that wraps the generic TTS service.
    """
    # Define the callback function that knows how to send data to a Twilio WebSocket
    async def send_to_twilio_ws(audio_chunk: bytes):
        await websocket.send_json({
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": base64.b64encode(audio_chunk).decode()}
        })

    # Call the generic TTS service with our specific callback
    await text_to_audio_stream(response_chunk_stream, send_to_twilio_ws)


# LANGGRAPH WORKFLOW
graph = create_graph()

transcribe_node = Node("transcribe", func=transcribe_audio, inputs=["audio_payload"], outputs=["transcription"])
graph.add_node(transcribe_node)

generate_node = Node(
    "generate",
    func=generate_gemini_response,
    inputs=["transcription", "system_prompt", "instructions", "context"],
    # The output is now a stream of chunks
    outputs=["response_chunk_stream"],
)
graph.add_node(generate_node)
graph.add_edge("transcribe", "generate")

tts_node = Node(
    "tts", 
    func=twilio_tts_handler, 
    # It now takes the stream of text chunks as input
    inputs=["response_chunk_stream", "websocket", "stream_sid"], 
    outputs=[]
)
graph.add_node(tts_node)
graph.add_edge("generate", "tts")

agent = create_react_agent(graph, llm_model=None)
builder = HandlerBuilder()


agent = create_react_agent(graph, llm_model=None)
builder = HandlerBuilder()

@builder.websocket("/media-stream")
async def media_stream(
    ws: WebSocket,
    request: Request,
    call_sid: str = Depends(lambda req: req.query_params.get("CallSid"))
):
    await ws.accept()
    logger.info(f"Call {call_sid} connected media-stream")

    session = await memory_manager.load_session(call_sid)
    # The system prompt is now static, but instructions/context are from the session
    system_prompt = DEFAULT_SYSTEM_PROMPT
    instructions = session.get("instructions", "")
    context = session.get("context", "")
    stream_sid = None

    try:
        async for msg in ws.iter_text():
            data = json.loads(msg)
            event = data.get("event")

            if event == "start":
                stream_sid = data['start']['streamSid']
                logger.info(f"Stream started: {stream_sid} for call {call_sid}")
            elif event == "media":
                if not stream_sid: continue
                payload = data["media"]["payload"]
                await agent.run(
                    inputs={
                        "audio_payload": payload,
                        "system_prompt": system_prompt,
                        "instructions": instructions,
                        "context": context,
                        "stream_sid": stream_sid,
                        "websocket": ws # Pass the websocket instance to the graph
                    }
                )
            elif event == "stop":
                logger.info(f"Call {call_sid} stop event received.")
                break
    except WebSocketDisconnect:
        logger.info(f"Call {call_sid} disconnected.")
    finally:
        await ws.close()
        logger.info(f"Websocket closed for call {call_sid}.")

builder.register(app)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/make-call")
async def make_call(
    request: Request,
    phone_number: str = Form(...),
    instructions: str = Form(...),
    context: str = Form("") # Context is optional
):
    try:
        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_NUMBER,
            # Pass the CallSid in the URL to link the call to the websocket session
            url=f"https://{request.headers['host']}/outgoing-call-twiml?CallSid={TWILIO_ACCOUNT_SID}",
            method="POST"
        )
        # Store the custom instructions and context in the memory session
        await memory_manager.create_session(call.sid, {
            "instructions": instructions,
            "context": context
        })
        return templates.TemplateResponse("call_initiated.html", {
            "request": request,
            "call_sid": call.sid,
            "status": "Dialing..."
        })
    except Exception as e:
        logger.error(f"Error making call: {e}")
        return HTMLResponse(f"<h1>Error</h1><p>Could not initiate call: {e}</p>", status_code=500)


@app.api_route("/outgoing-call-twiml", methods=["GET", "POST"])
async def outgoing_call_twiml(request: Request):
    resp = VoiceResponse()
    resp.say(voice="Polly.Joanna-Neural", message="Please wait a moment while we connect you.")
    connect = Connect()
    # Ensure CallSid from the request is passed to the websocket URL
    call_sid = request.query_params.get('CallSid')
    connect.stream(url=f"wss://{request.url.hostname}/media-stream?CallSid={call_sid}")
    resp.append(connect)
    return HTMLResponse(str(resp), media_type="application/xml")

@entrypoint(store=store)
def background_app(messages: list):
    return agent.invoke({"messages": messages})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
