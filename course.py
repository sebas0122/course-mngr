from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Course():
    __tablename__ = "course"

    id = int
    name = str
    faculty = int
    dependency = int
    ide = str
    course_id = int
    group = int
    type = str
    is_laboratory = bool
    semester = int
    theory_hours = int
    practice_hours = int
    tp_hours = int
    is_elective = bool
    is_department = bool
    schedule = str
    professor = list[int]
    room = str

    def __repr__(self) -> str:
        return f"Course id={self.id}, nombre={self.name}, codigo={self.faculty}{self.dependency}{self.course_id}, groupo={self.group}, tipo={self.type}, semestre={self.semester}, schedule={self.schedule}, profesor={self.professor}, room={self.room}"