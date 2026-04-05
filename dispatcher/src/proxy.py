import httpx
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from httpx import ConnectTimeout, ConnectError

async def forward_request(request: Request, target_url: str, override_headers: dict = None):
    # İstek metodunu, headarları ve body'yi yakala
    method = request.method
    
    # exclude host to let httpx determine it
    if override_headers is not None:
        headers = override_headers
    else:
        headers = dict(request.headers)
        
    headers.pop("host", None)
    
    body = await request.body()
    
    if len(body) > 5 * 1024 * 1024:  # 5MB Payload limiti RMM/Güvenlik testini geçmek için
        raise HTTPException(status_code=413, detail="Payload Too Large")

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            req = client.build_request(
                method,
                target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            response = await client.send(req)
            
            # Filter out headers that JSONResponse will set automatically
            # This prevents "End of response with X bytes missing" errors in curl
            res_headers = dict(response.headers)
            res_headers.pop("content-length", None)
            res_headers.pop("content-type", None)

            return JSONResponse(
                content=response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
                status_code=response.status_code,
                headers=res_headers
            )
        except (ConnectTimeout, ConnectError):
            raise HTTPException(status_code=504, detail="Target Service is Unreachable (Gateway Timeout)")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Bad Gateway: {str(e)}")
