from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from intake_agent.controller import router as query_router
from intake_agent.langchain_service import agent

app = FastAPI()

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="clara_pm/static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(query_router, prefix="")

@app.get("/")
async def serve_index():
    return FileResponse("clara_pm/static/index.html")