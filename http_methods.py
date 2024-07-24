import requests
import time

HTTP_METHODS = {
    "eth_blockNumber": {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    },
    "eth_getBlockByNumber": {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["latest", False],
        "id": 1
    },
    "eth_getBlockByHash": {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByHash",
        "params": ["0x1234...", False],
        "id": 1
    },
    "eth_getTransactionByHash": {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": ["0x1234..."],
        "id": 1
    },
    "eth_getTransactionReceipt": {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": ["0x1234..."],
        "id": 1
    },
    "eth_call": {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": "0x1234...",
            "data": "0x5678..."
        }, "latest"],
        "id": 1
    },
    "eth_sendRawTransaction": {
        "jsonrpc": "2.0",
        "method": "eth_sendRawTransaction",
        "params": ["0x1234..."],
        "id": 1
    },
    "eth_getBalance": {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": ["0x1234...", "latest"],
        "id": 1
    }
}

def http_request(http_url, duration, progress_bar, shared_metrics, method):
    start_time = time.time()
    
    request = HTTP_METHODS.get(method)
    if not request:
        raise ValueError("Unsupported HTTP method")
    
    while time.time() - start_time < duration * 60:
        try:
            response_start_time = time.time()
            response = requests.post(http_url, json=request)
            response_time = time.time() - response_start_time
            shared_metrics.append({"time": response_time, "status": "success" if response.status_code == 200 else "fail"})
            progress_bar.update()
        except Exception as e:
            shared_metrics.append({"time": 0, "status": "fail"})
            print(f"Error: {e}")
