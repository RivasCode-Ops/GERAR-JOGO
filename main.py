#!/usr/bin/env python3
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        from src.server import main as server_main
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        server_main(port)
    else:
        from src.cli import main
        main()
