
# WebSocket Benchmarking Tool

This tool allows you to benchmark WebSocket endpoints with multiple test scenarios. You can provide the test scenarios either through a YAML configuration file or via command-line parameters.

## Requirements

- Python 3.6+
- `websockets` library
- `tqdm` library
- `PyYAML` library

You can install the required libraries using pip:


pip install websockets tqdm pyyaml


## Usage

You can run the script either by specifying a configuration file or by providing individual parameters through the command line.

### Using a Configuration File

Create a YAML configuration file (e.g., `config.yaml`) with the following structure:

```yaml
scenarios:
  - url: "wss://url"
    duration: 5
    users: 2
    workers: 1
    method: "eth_subscribe"
  - url: "wss://url2"
    duration: 5
    users: 2
    workers: 1
    method: "eth_blockNumber"
  # Add more scenarios as needed
```

Run the script with the configuration file:

```sh
python benchmark.py -c config.yaml
```

### Using Command-Line Parameters

Alternatively, you can provide individual parameters via the command line:

```sh
python benchmark.py --url "wss://example.url" -t 5 -u 2 -w 1 -m "eth_subscribe"
```

### Parameters

- `-c, --config`: Path to the YAML configuration file.
- `--url`: WebSocket URL to test.
- `-t, --time`: Duration of the test in minutes.
- `-u, --users`: Number of concurrent users.
- `-w, --workers`: Number of workers.
- `-m, --method`: Web3 method to test (`eth_subscribe` or `eth_blockNumber`).

### Output

The script will generate a `metrics_statistics.csv` file with the results of the test scenarios. The CSV file will contain the following columns:

- `ws_url`: The WebSocket URL tested.
- `method`: The Web3 method used.
- `num_users`: Number of concurrent users.
- `num_workers`: Number of workers.
- `total_requests`: Total number of requests made.
- `max_response_time`: Maximum response time.
- `min_response_time`: Minimum response time.
- `avg_response_time`: Average response time.
- `test_duration_minutes`: Duration of the test in minutes.
- `failed_requests_number`: Number of failed requests.
- `failed_requests_percentage`: Percentage of failed requests.

## Example

### Example Configuration File (`config.yaml`)

```yaml
scenarios:
  - url: "wss://url1"
    duration: 5
    users: 2
    workers: 1
    method: "eth_subscribe"
  - url: "wss://url2"
    duration: 5
    users: 2
    workers: 1
    method: "eth_blockNumber"
```

### Running with Configuration File

```sh
python benchmark.py -c config.yaml
```

### Running with Command-Line Parameters

```sh
python benchmark.py --url "wss://url" -t 5 -u 2 -w 1 -m "eth_subscribe"
```

## License

This project is licensed under the MIT License.
```

Save this content to a `README.md` file in the same directory as your script. This file provides instructions on how to set up and use the WebSocket Benchmarking Tool.
