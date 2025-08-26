# from fastapi import Request, status, Depends
# from fastapi.responses import RedirectResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from . import oauth2, database

# PROTECTED_ROUTES = ["/account/archived", 
#                     "/account/favourite", 
#                     "/account/myads",
#                     "/account/profile/setting", 
#                     "/account/dashboard", 
#                     "/account/messages",
#                     "/ad/post-ad"] 
# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         path = request.url.path
#         if any(route in path for route in PROTECTED_ROUTES):
#             token = request.cookies.get("access_token")
#             if not token:
#                 return RedirectResponse(url="/users/login", status_code=status.HTTP_303_SEE_OTHER)

#             try:
#                 user = await oauth2.get_current_user(token, db=Depends(database.get_db))  
#             except Exception:
#                 return RedirectResponse(url="/users/login", status_code=status.HTTP_303_SEE_OTHER)
        
#         response = await call_next(request)
#         return response