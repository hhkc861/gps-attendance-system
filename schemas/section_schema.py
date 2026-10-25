from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class SectionCreateRequest(BaseModel):
    sectionCode: str = Field(
        min_length=1,
        title="Class section code",
        description="The class section code.",
        examples=["2627I_INT3105_1", "2526H_PHI1006_80"],
    )
    teachers: list[str] = Field(
        min_length=1,
        title="Teacher usernames",
        description="The usernames of teachers assigned to this section.",
        examples=[["tranmanhcuong"], ["tranmanhcuong", "hieuvd"]],
    )
    students: list[str] = Field(
        min_length=0,
        title="Student usernames",
        description="The usernames of students enrolled in this section.",
        examples=[["24021400", "24021393", "24021664"], []],
        default_factory=list,
    )

    @field_validator("teachers", "students")
    @classmethod
    def normalize_and_reject_duplicate_usernames(
        cls, usernames: list[str]
    ) -> list[str]:
        normalized_usernames = [username.strip() for username in usernames]
        if len(normalized_usernames) != len(set(normalized_usernames)):
            raise ValueError("Usernames in the same list must be unique")
        return normalized_usernames

    @model_validator(mode="after")
    def reject_users_with_both_roles(self):
        if set(self.teachers) & set(self.students):
            raise ValueError(
                "An account cannot be both a teacher and a student in the same section"
            )
        return self


class SectionCreateResponse(BaseModel):
    sectionId: int = Field(
        title="Class section ID",
        description="The unique ID of the newly created class section.",
        examples=[1, 2, 3],
    )
    sectionCode: str = Field(
        title="Class section code",
        description="The code of the newly created class section.",
        examples=["2627I_INT3105_1", "2526H_PHI1006_80"],
    )
    teachers: list[str] = Field(
        title="Teacher usernames",
        description="The usernames of teachers assigned to the class section.",
        examples=[["tranmanhcuong"], ["tranmanhcuong", "hieuvd"]],
    )
    students: list[str] = Field(
        title="Student usernames",
        description="The usernames of students added to the class section.",
        examples=[["24021400", "24021393", "24021664"], []],
    )
    createdAt: datetime = Field(
        title="Creation time",
        description="The time when the class section was created.",
        examples=["2026-10-25T19:39:44.104Z"],
    )
