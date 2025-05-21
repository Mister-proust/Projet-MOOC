from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse
from services.dashboard_users_cluster import get_all_usernames, get_similarity_scores

class UnauthorizedAccess(Exception):
    pass

# Init FastAPI
app = FastAPI()

@app.exception_handler(UnauthorizedAccess)
async def unauthorized_handler(request: Request, exc: UnauthorizedAccess):
    return templates.TemplateResponse("acces_refuse.html", {"request": request}, status_code=403)


# Dossiers
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "webapp/templates"
STATIC_DIR = BASE_DIR / "webapp/static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Simulation d'authentification simple
fake_users_db = {"admin": "password"}
session = {"user": None}

def login_required(request: Request):
    if not session["user"]:
        raise UnauthorizedAccess()
    return session["user"]


# === ROUTES GÉNÉRALES ===
@app.get("/")
async def accueil(request: Request):
    return templates.TemplateResponse("accueil.html", {"request": request, "user": session["user"]})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if fake_users_db.get(username) == password:
        session["user"] = username
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants incorrects"})

@app.get("/logout")
async def logout():
    session["user"] = None
    return RedirectResponse("/", status_code=303)

@app.get("/dashboard/question")
async def dashboard_question(request: Request, user: str = Depends(login_required)):
    return templates.TemplateResponse("dashboard_question.html", {"request": request, "user": user})

@app.get("/dashboard/thread")
async def dashboard_thread(request: Request, user: str = Depends(login_required)):
    return templates.TemplateResponse("dashboard_thread.html", {"request": request, "user": user})

@app.get("/dashboard/threads-cluster")
async def dashboard_threads_cluster(request: Request, user: str = Depends(login_required)):
    return templates.TemplateResponse("dashboard_threads_cluster.html", {"request": request, "user": user})

@app.get("/dashboard/users-cluster")
async def dashboard_users_cluster(request: Request, user: str = Depends(login_required), selected_user: str = None):
    users = get_all_usernames()
    resultats = None

    if selected_user:
        resultats = get_similarity_scores(selected_user)

    return templates.TemplateResponse("dashboard_users_cluster.html", {
        "request": request,
        "user": user,
        "users": users,
        "selected_user": selected_user,
        "resultats": resultats
    })
