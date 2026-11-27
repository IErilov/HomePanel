from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from data.documentation import NAV_SECTIONS, ENDPOINTS, BUCKET_TYPES, USER_TYPES
from data.profile import PROFILE

app = FastAPI(title="HomePanel Documentation", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "nav_sections": NAV_SECTIONS,
            "endpoint_count": len(ENDPOINTS),
            "group_count": len(NAV_SECTIONS),
        },
    )


@app.get("/api-reference", include_in_schema=False)
async def api_reference(request: Request):
    grouped = []
    for section in NAV_SECTIONS:
        items = [item for item in ENDPOINTS if item["group"] == section["id"]]
        grouped.append({**section, "endpoints": items})
    return templates.TemplateResponse(
        request=request,
        name="api_reference.html",
        context={"groups": grouped, "endpoint_count": len(ENDPOINTS)},
    )


@app.get("/api-reference/{slug}", include_in_schema=False)
async def endpoint_page(request: Request, slug: str):
    endpoint = next((item for item in ENDPOINTS if item["slug"] == slug), None)
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return templates.TemplateResponse(
        request=request,
        name="endpoint.html",
        context={"endpoint": endpoint},
    )


@app.get("/about", include_in_schema=False)
async def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={"profile": PROFILE},
    )


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
