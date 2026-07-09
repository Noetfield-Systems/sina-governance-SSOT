import argparse
import os
import sys
from http.server import ThreadingHTTPServer

from . import config as cfg
from .handler import Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description="NOOS Control Desk Phase 1 backend")
    parser.add_argument("--port", type=int, default=17877)
    parser.add_argument(
        "--repo-root",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    )
    args = parser.parse_args(argv)

    cfg.REPO_ROOT = os.path.abspath(args.repo_root)
    if not os.path.isfile(os.path.join(cfg.REPO_ROOT, cfg.REGISTRY_REL)):
        print(f"FATAL: no registry found at {os.path.join(cfg.REPO_ROOT, cfg.REGISTRY_REL)}", file=sys.stderr)
        sys.exit(2)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"NOOS Control Desk running at http://127.0.0.1:{args.port}  (repo root: {cfg.REPO_ROOT})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
