import uvicorn
import sys

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# static_directory = "frontend/public/assets"
# index_page = "frontend/index.html"

static_directory = "public/assets"
index_page = "public/index.html"


app.mount("/assets", StaticFiles(directory=static_directory), name="static")

@app.get("/", response_class=FileResponse)

def main():
    return index_page

if __name__ == "__main__" and len(sys.argv) > 1:
    match sys.argv[1]:
        case 'dev' | "--dev" | "-d":
            print("dev")
            uvicorn.run("main:app", port=8002, reload=True)
        case _:
            uvicorn.run("main:app", port=8002)