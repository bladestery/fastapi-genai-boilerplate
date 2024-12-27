"""Entry point to run the application"""

import uvicorn

from app.core.settings import settings

if __name__ == "__main__":
    # Configure app settings for development or production
    uvicorn.run(
        app="app.core.server:app",
        host=settings.host,
        port=settings.port,
        workers=settings.worker_count,
        reload=settings.environment != "production",
    )
