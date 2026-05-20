import logging
from fastapi import APIRouter, HTTPException, status
from config import BASE_API_PREFIX, MODEL_NAME
from app.models.comment_model import CommentRequest, CommentResponse
from app.services.ai_service import generate_comment

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{BASE_API_PREFIX}/comment", tags=["Comments"])


@router.post(
    "/generate",
    response_model=CommentResponse,
    summary="Generate a documentation comment",
    description="Accepts source code and returns a properly formatted documentation comment for the detected language.",
    status_code=status.HTTP_200_OK,
)
async def generate_ai_comment(request: CommentRequest) -> CommentResponse:
    """
    Generate a documentation comment for the provided code snippet.

    Args:
        request: CommentRequest containing code, language, and comment_style.

    Returns:
        CommentResponse with the generated comment.

    Raises:
        HTTPException 422: If code is empty or too long.
        HTTPException 503: If the LLM backend is unavailable or times out.
        HTTPException 500: On unexpected internal errors.
    """
    try:
        logger.info(
            "Generating comment for language=%s length=%d",
            request.language,
            len(request.code),
        )
        comment = await generate_comment(
            code=request.code,
            language=request.language,
            comment_style=request.comment_style,
            model=request.model,
            temperature=request.temperature,
            tokens=request.tokens,
        )

        return CommentResponse(
            comment=comment,
            language=request.language,
            model=MODEL_NAME,
        )

    except RuntimeError as exc:
        error_msg = str(exc)
        logger.error("LLM service error: %s", error_msg)

        if (
            "timeout" in error_msg.lower()
            or "connection" in error_msg.lower()
            or "attempts" in error_msg.lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service unavailable: {error_msg}",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {error_msg}",
        )

    except Exception as exc:
        logger.exception("Unexpected error in generate_ai_comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(exc)}",
        )
