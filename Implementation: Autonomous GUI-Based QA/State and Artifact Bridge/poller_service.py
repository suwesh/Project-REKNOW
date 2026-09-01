import signal
import sys
from ms_graphapi_poller import poll_run_states
from your_app import RAG_RESOURCES  # reuse already-loaded resources/ change this as per your implementation of domain knowledge retrieval

def shutdown_handler(signum, frame):
    print("Poller shutting down gracefully...")
    sys.exit(0)

# handle SIGTERM / SIGINT
signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

if __name__ == "__main__":
    print("Starting QA Root Poller...")
    poll_run_states(RAG_RESOURCES)
