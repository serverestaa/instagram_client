from fastapi import HTTPException, APIRouter
from db.db_search import search_in_es

router = APIRouter(
    prefix='/search',
    tags=['search']
)


@router.get("/")
def search_endpoint(query: str):
    try:
        results = search_in_es(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))