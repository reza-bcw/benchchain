import asyncio
import json
import websockets
import csv
import time
import argparse
import yaml
from statistics import mean
from tqdm import tqdm
import concurrent.futures
from multiprocessing import Manager

async def subscribe(ws_url, duration, progress_bar, shared_metrics, method):
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
        elif method == "eth_blockNumber":
            request = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }
        
        await websocket.send(json.dumps(request))
        
        # Wait for the response
        response = await websocket.recv()
        if isinstance(response, bytes):
            response = response.decode('utf-8')
        response_time = time.time() - start_time
        shared_metrics.append({"time": response_time, "status": "success" if "result" in response else "fail"})
        
        # Continuously receive messages for eth_subscribe
        if method == "eth_subscribe":
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
        else:
            progress_bar.update()

async def run_tasks(ws_url, duration, num_users, progress_bar, shared_metrics, method):
    tasks = [asyncio.create_task(subscribe(ws_url, duration, progress_bar, shared_metrics, method)) for _ in range(num_users)]
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

def worker(ws_url, duration, num_users, total_updates, shared_metrics, method):
    progress_bar = tqdm(total=total_updates, desc="Running Test", unit="req")
    asyncio.run(run_tasks(ws_url, duration, num_users, progress_bar, shared_metrics, method))
    progress_bar.close()

def run_test_scenario(ws_url, duration, num_users, num_workers, method):
    total_updates = duration * 60 * num_users * (1 if method != "eth_subscribe" else num_workers)  # Estimate the number of updates for progress bar
    
    with Manager() as manager:
        shared_metrics = manager.list()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, ws_url, duration, num_users, total_updates // num_workers, shared_metrics, method) for _ in range(num_workers)]
            concurrent.futures.wait(futures)
        
        # Calculate metrics
        response_times = [m["time"] for m in shared_metrics if m["status"] == "success"]
        num_requests = len(shared_metrics)
        num_success_requests = len(response_times)
        num_failed_requests = num_requests - num_success_requests
        failed_requests_percentage = (num_failed_requests / num_requests) * 100 if num_requests else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        avg_response_time = mean(response_times) if response_times else 0
        
        return {
            "ws_url": ws_url,
            "method": method,
            "num_users": num_users,
            "num_workers": num_workers,
            "total_requests": num_requests,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "avg_response_time": avg_response_time,
            "test_duration_minutes": duration,
            "failed_requests_number": num_failed_requests,
            "failed_requests_percentage": failed_requests_percentage
        }

def main(config_file=None, ws_url=None, duration=None, num_users=None, num_workers=None, method=None):
    if config_file:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        scenarios = config['scenarios']
    else:
        if not all([ws_url, duration, num_users, num_workers, method]):
            raise ValueError("All parameters must be provided if config file is not used")
        
        scenarios = [{
            'url': ws_url,
            'duration': duration,
            'users': num_users,
            'workers': num_workers,
            'method': method
        }]
    
    results = []
    for scenario in scenarios:
        result = run_test_scenario(
            scenario['url'],
            scenario['duration'],
            scenario['users'],
            scenario['workers'],
            scenario['method']
        )
        results.append(result)
    
    # Save results to CSV
    with open("metrics_statistics.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "ws_url",
            "method",
            "num_users",
            "num_workers",
            "total_requests",
            "max_response_time",
            "min_response_time",
            "avg_response_time",
            "test_duration_minutes",
            "failed_requests_number",
            "failed_requests_percentage"
        ])
        for result in results:
            writer.writerow([
                result["ws_url"],
                result["method"],
                result["num_users"],
                result["num_workers"],
                result["total_requests"],
                result["max_response_time"],
                result["min_response_time"],
                result["avg_response_time"],
                result["test_duration_minutes"],
                result["failed_requests_number"],
                result["failed_requests_percentage"]
            ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebSocket Benchmarking Tool')
    parser.add_argument('-c', '--config', type=str, help='Path to the YAML configuration file')
    parser.add_argument('--url', type=str, help='WebSocket URL to test')
    parser.add_argument('-t', '--time', type=int, help='Duration of the test in minutes')
    parser.add_argument('-u', '--users', type=int, help='Number of concurrent users')
    parser.add_argument('-w', '--workers', type=int, help='Number of workers')
    parser.add_argument('-m', '--method', type=str, choices=['eth_subscribe', 'eth_blockNumber'], help='Web3 method to test')
    
    args = parser.parse_args()
    
    main(args.config, args.url, args.time, args.users, args.workers, args.method)
