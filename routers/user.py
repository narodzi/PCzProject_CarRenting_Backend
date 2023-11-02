from fastapi import APIRouter, Request, Response, Body, status
from starlette.responses import JSONResponse
from starlette.status import HTTP_204_NO_CONTENT

from models.user import User, UserUpdate

router = APIRouter()


@router.get("/", response_description="List all users")
def get_users(request: Request):
    users = list(request.app.database['Users'].find(limit=1000))
    return users


@router.get("/{id}", response_description="Show a user")
def get_user(request: Request, id: str):
    user = request.app.database['Users'].find_one(
        {"_id": id}
    )
    if not user:
        return JSONResponse(content={"detail": f"User {id} does not exist"}, status_code=404)
    return user


@router.post("/", response_description="Add a user")
def add_user(request: Request, user: User = Body(...)):
    user = user.dict()
    new_user = request.app.database['Users'].insert_one(user)
    created_user = request.app.database['Users'].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user


@router.put("/{id}", response_description="Update a user")
def update_user(request: Request, id: str, user: UserUpdate = Body(...)):
    user_data = user.dict(exclude_unset=True)

    update_result = request.app.database['Users'].update_one(
        {"_id": id}, {"$set": user_data}
    )

    if update_result.modified_count == 1:
        updated_user = request.app.database['Users'].find_one({'_id': id})
        return updated_user
    if update_result.matched_count == 1:
        return JSONResponse(content={"detail": f"User {id} has not been updated"}, status_code=400)
    return JSONResponse(content={"detail": f"User {id} not found"}, status_code=404)


@router.delete("/{id}", response_description="Delete a user")
def delete_user(request: Request, id: str):
    deleted_user = request.app.database['Users'].delete_one(
        {"_id": id}
    )
    if deleted_user.deleted_count == 0:
        return JSONResponse(content={"detail": f"User {id} does not exist"}, status_code=404)
    return Response(status_code=HTTP_204_NO_CONTENT)
