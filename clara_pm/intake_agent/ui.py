from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .intake_agent import handle_message

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/chat", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/chat", response_class=HTMLResponse)
async def post_chat(request: Request):
    form = await request.form()
    user_id = form.get("user_id")
    message = form.get("message")
    response = await handle_message(Message(user_id=user_id, message=message))
    return templates.TemplateResponse("chat.html", {"request": request, "response": response}) 