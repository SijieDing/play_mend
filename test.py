import bjoern
def run_bjoern_server(app, host='127.0.0.1', port=8000):
    """Run the Bjoern server in a separate thread."""
    try:
        bjoern.run(app, host, port, reuse_port=True)
    except KeyboardInterrupt:
        # Handle Ctrl+C within the server thread
        print("Server interrupted, shutting down...")
    finally:
        print("Bjoern server stopped") 
run_bjoern_server(None)