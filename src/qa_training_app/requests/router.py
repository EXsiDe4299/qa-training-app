from fastapi import APIRouter, Depends, HTTPException

from qa_training_app.auth.deps import get_current_user_id
from qa_training_app.db import get_db
from qa_training_app.requests.repository import RequestRepository
from qa_training_app.requests.schemas import CreateRequest, RequestResponse
from qa_training_app.requests.service import (
    RequestNotFoundError,
    RequestPermissionError,
    RequestService,
)

router = APIRouter(
    prefix="/requests",
    tags=["requests"],
)


@router.get("", response_model=list[RequestResponse])
def get_requests(_user_id: int = Depends(get_current_user_id)):
    with get_db() as conn:
        repository = RequestRepository(conn)
        service = RequestService(repository)
        requests = service.get_all()

    return requests


@router.post("", status_code=201, response_model=RequestResponse)
def create_request(
    data: CreateRequest,
    user_id: int = Depends(get_current_user_id),
):
    with get_db() as conn:
        repository = RequestRepository(conn)
        service = RequestService(repository)

        try:
            return service.create(
                title=data.title,
                description=data.description,
                author_id=user_id,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            )


@router.get("/{request_id}", response_model=RequestResponse)
def get_request(
    request_id: int,
    _user_id: int = Depends(get_current_user_id),
):
    with get_db() as conn:
        repository = RequestRepository(conn)
        service = RequestService(repository)
        request_item = service.get_by_id(request_id)

    if request_item is None:
        raise HTTPException(
            status_code=404,
            detail="Request not found",
        )

    return request_item


@router.delete("/{request_id}")
def delete_request(
    request_id: int,
    user_id: int = Depends(get_current_user_id),
):
    with get_db() as conn:
        repository = RequestRepository(conn)
        service = RequestService(repository)

        try:
            service.delete(
                request_id=request_id,
                user_id=user_id,
            )
        except RequestNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Request not found",
            )
        except RequestPermissionError:
            raise HTTPException(
                status_code=403,
                detail="You cannot delete this request",
            )

    return {"message": "Request deleted"}
