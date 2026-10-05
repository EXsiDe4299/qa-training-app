from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

FRONTEND_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="requests.html",
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
    )


@router.get("/requests", response_class=HTMLResponse)
def requests_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="requests.html",
    )
