# middlewares/auth_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from services.auth_service import AuthService
from services.supabase_service import SupabaseService

auth_service = AuthService()
sb_service = SupabaseService()

class AttachUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Reset mặc định
        request.state.user = None
        request.state.token = None

        # Lấy Bearer token từ header
        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                # ✅ Verify JWT → lấy user (ít nhất có 'id')
                user = await auth_service.verify_token(token)
                if user and user.get("id"):
                    # Gắn vào request.state cho route dùng
                    request.state.user = {"id": user["id"], "email": user.get("email")}
                    request.state.token = token

                    # ✅ RẤT QUAN TRỌNG: set JWT vào Supabase client để qua RLS
                    # (Sau lệnh này, mọi gọi sb_service.client.table(...).select() sẽ chạy với JWT user)
                    sb_service.set_auth_token(token)

                    print(f"✅ Middleware attached user: {user['id']}")
                else:
                    print("⚠️ Middleware: token verified but user missing 'id'")
            except Exception as e:
                print(f"❌ Middleware token invalid: {e}")

        # Tiếp tục chuỗi middleware
        return await call_next(request)
