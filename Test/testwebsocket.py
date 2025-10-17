import aiohttp
import asyncio
import os
import json
from colorama import Fore, Style, init

# Initialize colors for cross-platform terminal output
init(autoreset=True)

BASE_URL = "ws://localhost:8000"

UPLOAD_PATH = "/v1/translate/ws/upload/fce1b0d5-cb7e-4ecc-acad-265283bfd001?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cGxvYWRfaWQiOiJmY2UxYjBkNS1jYjdlLTRlY2MtYWNhZC0yNjUyODNiZmQwMDEiLCJ1c2VyX2lkIjoxLCJwcm9qZWN0X2lkIjoxLCJleHAiOjE3NjAzMDQwNTAsInR5cGUiOiJ1cGxvYWQifQ.dt0xiMrW9g_ho96cbUb7UoiA_wP5_LEwvyz8KKdLs8M"
LOGS_PATH   = "/v1/translate/ws/logs/fce1b0d5-cb7e-4ecc-acad-265283bfd001?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cGxvYWRfaWQiOiJmY2UxYjBkNS1jYjdlLTRlY2MtYWNhZC0yNjUyODNiZmQwMDEiLCJ1c2VyX2lkIjoxLCJwcm9qZWN0X2lkIjoxLCJleHAiOjE3NjAzMDQwNTAsInR5cGUiOiJ1cGxvYWQifQ.dt0xiMrW9g_ho96cbUb7UoiA_wP5_LEwvyz8KKdLs8M"
CHUNK_SIZE = 1024 * 1024  # 1 MB
TOTAL_SIZE = 10000 * 1024 * 1024  # 100 MB

# Shared events
start_event = asyncio.Event()
stop_event = asyncio.Event()


async def read_logs(session):
    """Listen to the logs websocket and coordinate upload start/stop."""
    logs_url = f"{BASE_URL}{LOGS_PATH}"
    print(f"{Fore.CYAN}[+] Connecting to logs: {logs_url}{Style.RESET_ALL}")

    async with session.ws_connect(logs_url) as ws:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    print(f"{Fore.YELLOW}[LOG] {msg.data}{Style.RESET_ALL}")
                    continue

                msg_type = data.get("type")

                # Handle message types
                if msg_type == "status":
                    print(
                        f"{Fore.CYAN}[STATUS] {data.get('status', '-')}, "
                        f"Progress: {data.get('progress', 0):.2f}% "
                        f"({data.get('bytes_received', 0) / 1024 / 1024:.1f} MB){Style.RESET_ALL}"
                    )
                    if not start_event.is_set():
                        start_event.set()  # allow uploader to start

                elif msg_type == "progress":
                    progress = data.get("progress", 0)
                    bytes_received = data.get("bytes_received", 0)
                    print(f"{Fore.BLUE}[PROGRESS] {progress:.2f}% ({bytes_received / 1024 / 1024:.1f} MB){Style.RESET_ALL}")

                elif msg_type == "complete":
                    print(f"{Fore.GREEN}[COMPLETE] {data.get('message', 'Upload completed!')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Project ID: {data.get('project_id', '-')}{Style.RESET_ALL}")
                    stop_event.set()
                    break

                elif msg_type == "error":
                    print(f"{Fore.RED}[ERROR] {data.get('message', 'Unknown error')}{Style.RESET_ALL}")
                    stop_event.set()
                    break

                else:
                    print(f"{Fore.YELLOW}[LOG] {msg.data}{Style.RESET_ALL}")

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"{Fore.RED}[!] Logs error: {msg.data}{Style.RESET_ALL}")
                stop_event.set()
                break


async def upload_data(session):
    """Wait until 'status' message received, then start sending chunks."""
    upload_url = f"{BASE_URL}{UPLOAD_PATH}"
    print(f"{Fore.CYAN}[+] Waiting for status message before upload...{Style.RESET_ALL}")

    # Wait until server signals we can start uploading
    await start_event.wait()

    print(f"{Fore.CYAN}[+] Connecting to upload: {upload_url}{Style.RESET_ALL}")

    async with session.ws_connect(upload_url, max_msg_size=0) as ws:
        # Step 1: send metadata
        metadata = {"file_extension": "mp4"}
        await ws.send_str(json.dumps(metadata))

        sent = 0
        chunk = os.urandom(CHUNK_SIZE)
        print(f"{Fore.CYAN}[+] Upload started...{Style.RESET_ALL}")

        while sent < TOTAL_SIZE:
            if stop_event.is_set():  # stop immediately on complete/error
                print(f"{Fore.YELLOW}[UPLOAD] Stopped by server signal.{Style.RESET_ALL}")
                break

            await ws.send_bytes(chunk)
            sent += CHUNK_SIZE
            percent = (sent / TOTAL_SIZE) * 100
            print(f"{Fore.MAGENTA}[UPLOAD] Sent {sent / 1024 / 1024:.1f} MB ({percent:.2f}%){Style.RESET_ALL}")

        if not stop_event.is_set():
            print(f"{Fore.CYAN}[+] Upload finished sending data.{Style.RESET_ALL}")

        await ws.close()


async def main():
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            read_logs(session),
            upload_data(session),
        )


if __name__ == "__main__":
    asyncio.run(main())
