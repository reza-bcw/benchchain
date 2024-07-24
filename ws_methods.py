import asyncio
import json
import websockets
import time

async def ws_subscribe(ws_url, duration, progress_bar, shared_metrics, method):
    async with websockets.connect(ws_url) as websocket:
        start_time = time.time()
        
        # Send the request based on the method
        if method == "eth_subscribe":
            request = {
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": ["newHeads"],
                "id": 1
            }
        else:
            raise ValueError("Unsupported WebSocket method")
        
        await websocket.send(json.dumps(request))
        
        # Wait for the response
        response = await websocket.recv()
        if isinstance(response, bytes):
            response = response.decode('utf-8')
        response_time = time.time() - start_time
        shared_metrics.append({"time": response_time, "status": "success" if "result" in response else "fail"})
        
        # Continuously receive messages for eth_subscribe
        while time.time() - start_time < duration * 60:
            try:
                message_start_time = time.time()
                message = await websocket.recv()
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                message_response_time = time.time() - message_start_time
                shared_metrics.append({"time": message_response_time, "status": "success"})
                # Update the progress bar
                progress_bar.update()
            except Exception as e:
                shared_metrics.append({"time": 0, "status": "fail"})
                print(f"Error: {e}")
