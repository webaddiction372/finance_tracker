from pathlib import Path

from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404


def serve_static(request, path):
    resolved = finders.find(path)
    if not resolved:
        raise Http404("Static file not found.")

    if isinstance(resolved, (list, tuple)):
        resolved = resolved[0]

    file_path = Path(resolved)
    if not file_path.exists() or not file_path.is_file():
        raise Http404("Static file not found.")

    return FileResponse(file_path.open("rb"))
