import asyncio
from edge_tts import Communicate

async def main():
    try:
        communicate = Communicate("Testing Text-to-Speech", "en-US-AriaNeural")
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        print(f"Success, generated {len(chunks)} chunks of audio")
    except Exception as e:
        print(f"Failed: {e}")

asyncio.run(main())
