#!/usr/bin/env python3
"""Stub metrics server for Qdrant (Day19) and Llama.cpp (Day20).

Exposes fake Prometheus metrics on port 9101 so Prometheus can scrape them
even when the real services are not running.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import random
import time

METRICS = """# HELP qdrant_collections_total Number of collections
# TYPE qdrant_collections_total gauge
qdrant_collections_total 3

# HELP qdrant_vectors_total Total number of vectors across all collections
# TYPE qdrant_vectors_total gauge
qdrant_vectors_total {vectors}

# HELP qdrant_pending_operations Number of pending operations
# TYPE qdrant_pending_operations gauge
qdrant_pending_operations 0

# HELP qdrant_memory_allocated_bytes Allocated memory in bytes
# TYPE qdrant_memory_allocated_bytes gauge
qdrant_memory_allocated_bytes {memory}

# HELP llamacpp_requests_total Total number of inference requests
# TYPE llamacpp_requests_total counter
llamacpp_requests_total 1523

# HELP llamacpp_tokens_total Total tokens generated
# TYPE llamacpp_tokens_total counter
llamacpp_tokens_total 89456

# HELP llamacpp_queue_size Current queue size
# TYPE llamacpp_queue_size gauge
llamacpp_queue_size 0

# HELP llamacpp_inference_duration_seconds_seconds Inference duration histogram
# TYPE llamacpp_inference_duration_seconds_seconds histogram
llamacpp_inference_duration_seconds_seconds_bucket{{le="0.1"}} 1200
llamacpp_inference_duration_seconds_seconds_bucket{{le="0.5"}} 1450
llamacpp_inference_duration_seconds_seconds_bucket{{le="1.0"}} 1500
llamacpp_inference_duration_seconds_seconds_bucket{{le="+Inf"}} 1523
llamacpp_inference_duration_seconds_seconds_sum 456.7
llamacpp_inference_duration_seconds_seconds_count 1523
"""


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            vectors = int(50000 + random.random() * 10000)
            memory = int(256 * 1024 * 1024 + random.random() * 64 * 1024 * 1024)
            response = METRICS.format(vectors=vectors, memory=memory)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logs


def main():
    port = 9101
    server = HTTPServer(("0.0.0.0", port), MetricsHandler)
    print(f"Stub metrics server running on :{port}")
    print(f"Metrics available at: http://localhost:{port}/metrics")
    server.serve_forever()


if __name__ == "__main__":
    main()
