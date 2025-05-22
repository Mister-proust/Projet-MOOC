from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse
from services.dashboard_threads_cluster import get_all_clusters, get_messages_by_topic,  get_bertopic_html
from pydantic import BaseModel
from services.dashboard_users_cluster import get_all_usernames, get_similarity_scores
from services.dashboard_question import search_similar_message

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

class Query(BaseModel):
    text: str

class ThreadQuery(BaseModel):
    title: str
    course_id: str

@app.post("/dashboard/question")
def search(query: Query):
    result = search_similar_message(query.text)

    if result:
        # Conversion des champs non JSON-compatibles
        result["id"] = str(result["id"])
        result["course_id"] = str(result["course_id"])
        result["created_at"] = result["created_at"].isoformat()  # Convertit datetime en chaîne ISO

        return JSONResponse(content={"message": result})
    else:
        return JSONResponse(content={"message": "Aucun résultat trouvé."})

@app.post("/dashboard/threadquestion")
def get_thread(query: ThreadQuery):
    """Récupère tous les messages d'un fil de discussion"""
    from services.dashboard_question import get_thread_messages  # Assurez-vous d'importer la fonction
    
    messages = get_thread_messages(query.title, query.course_id)
    
    if messages:
        # Conversion des champs non JSON-compatibles pour chaque message
        for message in messages:
            message["id"] = str(message["id"])
            message["course_id"] = str(message["course_id"])
            message["created_at"] = message["created_at"].isoformat()
        
        return JSONResponse(content={"messages": messages})
    else:
        return JSONResponse(content={"messages": []})

@app.get("/dashboard/thread")
async def dashboard_thread_get(request: Request, user: str = Depends(login_required)):
    courses = get_all_courses()
    return templates.TemplateResponse("dashboard_thread.html", {
        "request": request,
        "user": user,
        "courses": courses,
        "threads": [],
        "selected_course": None,
        "selected_thread": None,
        "messages": None
    })

@app.post("/dashboard/thread")
async def dashboard_thread_post(request: Request, user: str = Depends(login_required)):
    form = await request.form()
    selected_course = form.get("selected_course")
    selected_thread = form.get("selected_thread")

    courses = get_all_courses()
    threads = get_threads_for_course(selected_course) if selected_course else []

    messages = None
    if selected_thread:
        messages = get_thread_with_messages(selected_thread)

    return templates.TemplateResponse("dashboard_thread.html", {
        "request": request,
        "user": user,
        "courses": courses,
        "threads": threads,
        "selected_course": selected_course,
        "selected_thread": selected_thread,
        "messages": messages
    })

@app.get("/dashboard/threads-cluster")
async def dashboard_threads_cluster(request: Request, user: str = Depends(login_required)):
    clusters = get_all_clusters()
    plot_html = get_bertopic_html()
    return templates.TemplateResponse(
        "dashboard_threads_cluster.html",
        {"request": request, "user": user, "topics": clusters, "plot_html": plot_html}
    )

@app.get("/dashboard/threads-cluster/{topic_id}")
def get_cluster_messages(topic_id: int):
    return get_messages_by_topic(topic_id)

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
