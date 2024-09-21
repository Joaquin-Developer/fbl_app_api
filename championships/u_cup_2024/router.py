from fastapi import APIRouter, Response


router = APIRouter()


@router.get("/")
def main():
    return Response(content="Hello World!", status_code=200)
