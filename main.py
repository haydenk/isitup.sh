from socket import create_connection
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel


app = FastAPI(docs_url=None, redoc_url=None)
origins = ["www.isitup.sh", "haydenk.github.io", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class DomainRequest(BaseModel):
    host: str
    port: int = 443


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
async def read_root(request: Request, domain: str):
    status: bool = False
    host: str = domain
    port: int = 443
    if ";" in domain:
        host, port = domain.split(";")

    status = check_host(host, port)
    if port == 443 and not status:
        status = check_host(host, 80)
    
    user_agent = request.headers.get("user-agent")
    accept = request.headers.get("accept")

    if accept == "text/plain" or "curl" in user_agent:
        up_or_down: str = "up" if status else "down"
        message: str = f"{host} appears to be {up_or_down}"
        if ";" in domain:
            message = f"{host}:{port} appears to be {up_or_down}"

        return PlainTextResponse(message)

    return {
        "host": host,
        "port": port,
        "status": status,
    }


@app.post("/")
async def post_root(body: DomainRequest):
    status: bool = False

    status = check_host(body.host, body.port)
    if body.port == 443 and not status:
        status = check_host(body.host, 80)    

    return {
        "host": body.host,
        "port": body.port,
        "status": status
    }

