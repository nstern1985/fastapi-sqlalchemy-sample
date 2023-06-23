import uvicorn
from starlette.middleware.cors import CORSMiddleware
from routes.employees.v1.get import router as get_router
from routes.employees.v1.put import router as put_router
from routes.employees.v1.post import router as post_router
from routes.employees.v1.delete import router as delete_router
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse
from settings import settings

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# region routers
app.include_router(get_router)
app.include_router(put_router)
app.include_router(post_router)
app.include_router(delete_router)
# endregion
# region add_middlewares
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], expose_headers=["*"])
# endregion

# region secure api doc

API_KEY = settings.SWAGGER_API_KEY
API_KEY_NAME = "apiKey"
COOKIE_DOMAIN = "clarity.io"


async def get_api_key(api_key_query: str = Security(APIKeyQuery(name=API_KEY_NAME, auto_error=False)),
                      api_key_header: str = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=False)),
                      api_key_cookie: str = Security(APIKeyCookie(name=API_KEY_NAME, auto_error=False))) -> str:
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")


@app.get("/logout", tags=["documentation"])
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie(API_KEY_NAME, domain=COOKIE_DOMAIN)
    return response


@app.get("/openapi.json", tags=["documentation"])
async def get_open_api_endpoint(api_key: APIKey = Depends(get_api_key)):
    response = JSONResponse(get_openapi(title="Employee-Manager-API", version="1.0", routes=app.routes))
    return response


@app.get("/docs", tags=["documentation"])
async def get_documentation(api_key: str = Depends(get_api_key)):
    response = get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
    response.set_cookie(
        API_KEY_NAME,
        value=api_key,
        # domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
