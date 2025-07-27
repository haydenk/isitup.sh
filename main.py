from socket import create_connection
from typing import Annotated
from urllib.error import URLError
from urllib.parse import urlparse
from fastapi import FastAPI, Query

app = FastAPI(docs_url=None, redoc_url=None)


def check_host(domain: str, port: int) -> bool:
    try:
        create_connection((domain, port), timeout=10)
        return True
    except TimeoutError:
        pass
    except Exception:
        pass

    return False


@app.get("/{domain}")
def read_root(domain: str, port: Annotated[int, Query()] = 443):
    status: bool = False

    status = check_host(domain, port)
    if port == 443 and not status:
        status = check_host(domain, 80)    

    return {
        "domain": domain,
        "port": port,
        "status": status
    }
