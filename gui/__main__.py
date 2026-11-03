"""Start the web interface from the project root: python -m gui"""
import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Marauders Map web interface")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    print(f"Marauders Map: http://127.0.0.1:{args.port}")
    # Local use only: no authentication, so never bind to another interface.
    uvicorn.run("gui.app:app", host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
