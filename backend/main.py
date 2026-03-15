from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.courses import router as courses_router
from routes.clubs import router as clubs_router
from routes.research import router as research_router
from routes.events import router as events_router
from routes.dining import router as dining_router
from routes.search import router as search_router
from routes.stats import router as stats_router

app = FastAPI(
    title="UNC Resource Engine",
    description="Distributed campus resource API with consistent hashing, Redis cache-aside, and 2-replica writes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses_router)
app.include_router(clubs_router)
app.include_router(research_router)
app.include_router(events_router)
app.include_router(dining_router)
app.include_router(search_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {
        "app": "UNC Resource Engine",
        "university": "University of North Carolina at Chapel Hill",
        "version": "1.0.0",
        "endpoints": [
            "/courses", "/clubs", "/research",
            "/events", "/dining", "/search", "/stats", "/stats/ring",
        ],
    }


@app.get("/health")
def health():
    from cache import REDIS_AVAILABLE
    return {"status": "ok", "redis": REDIS_AVAILABLE}
