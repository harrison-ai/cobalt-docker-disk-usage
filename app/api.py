import uvicorn
import utils
from config import Config
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/metrics")
async def read_metrics():
    metrics = []
    data = utils.read_usage()
    for export_name, export_data in data["exports"].items():
        for folder_name, folder_data in export_data["folders"].items():
            folder_size = folder_data["bytes"]
            metrics.append(
                f'folder_size_bytes{{export="{export_name}", folder="{folder_name}"}} {folder_size}'
            )
    response = "\n".join(metrics)
    return PlainTextResponse(response)


if __name__ == "__main__":
    c = Config()
    uvicorn.run(
        "api:app",
        host=c.get("API_HOST"),
        port=c.get("API_PORT"),
        workers=c.get("API_WORKERS"),
        log_level="info",
    )
