from pydantic import BaseModel, Field, field_validator


class CommentRequest(BaseModel):

    code: str = Field(
        ..., min_length=1, max_length=8000, description="Source code to document"
    )

    language: str = Field(
        ..., min_length=1, max_length=50, description="Language identifier"
    )

    comment_style: str = Field(..., max_length=20, description="Comment style hint")

    model: str | None = None

    temperature: float | None = None

    tokens: int | None = None

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, v: str) -> str:

        if not v.strip():
            raise ValueError("code must not be empty")

        return v

    @field_validator("language")
    @classmethod
    def normalize_language(cls, v: str) -> str:

        return v.strip().lower()


class CommentResponse(BaseModel):
    comment: str = Field(..., description="Generated documentation comment")
    language: str = Field(..., description="Language the comment was generated for")
    model: str = Field(..., description="LLM model used for generation")
