from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
import httpx
import logging
from api_gateway.config import SERVICE_REGISTRY

router = APIRouter()
logger = logging.getLogger(__name__)

class ServiceProxy:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def proxy_request(self, service_name: str, path: str, request: Request) -> JSONResponse:
        service_url = SERVICE_REGISTRY.get(service_name)
        if not service_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_name}' not found"
            )
        
        target_url = f"{service_url}/{path}" if path else service_url
        body = await request.body()
        
        headers = {
            k: v for k, v in request.headers.items() 
            if k.lower() not in ['host', 'content-length']
        }
        
        try:
            logger.info(f"Proxying {request.method} {target_url}")
            
            response = await self.client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                content=body,
                headers=headers
            )
            
            if response.headers.get("content-type", "").startswith("application/json"):
                content = response.json()
            else:
                content = {"data": response.text}
            
            return JSONResponse(
                content=content,
                status_code=response.status_code
            )
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service '{service_name}' unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def close(self):
        await self.client.aclose()

service_proxy = ServiceProxy()

@router.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service_name: str, path: str, request: Request):
    return await service_proxy.proxy_request(service_name, path, request)

@router.api_route("/{service_name}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service_root(service_name: str, request: Request):
    return await service_proxy.proxy_request(service_name, "", request)