from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        # StaticFiles normalizes URLs to native separators on Windows.
        route = path.replace('\\', '/').lstrip('/')
        if route == 'api' or route.startswith('api/'):
            raise HTTPException(404, '接口不存在')
        try:
            return await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code != 404 or Path(path).suffix:
                raise
            return FileResponse(Path(self.directory) / 'index.html')
