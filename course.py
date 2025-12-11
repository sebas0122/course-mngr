from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column
from sqlalchemy import ARRAY, Integer


class Course(SQLModel, table=True):
    """
    Course model representing the 'materias' table in the database.
    """
    __tablename__ = "materias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(description="Course name")
    facultad: int = Field(description="Faculty code")
    dependencia: int = Field(description="Dependency code")
    ide: str = Field(description="IDE identifier")
    materia: int = Field(description="Course/subject code")
    grupo: int = Field(description="Group number")
    tipo: str = Field(description="Course type (T-P, etc.)")
    es_lab: bool = Field(description="Is laboratory", alias="is_laboratory")
    nivel: int = Field(description="Semester/level")
    horas_teoricas: int = Field(description="Theory hours")
    horas_practicas: int = Field(description="Practice hours")
    horas_tp: int = Field(description="TP hours")
    electiva: bool = Field(description="Is elective")
    es_dept: bool = Field(description="Is department course")
    horario: str = Field(description="Schedule string (e.g., 'L16-18|M8-10')")
    profesor: List[int] = Field(default_factory=list, sa_column=Column(ARRAY(Integer)), description="List of professor IDs")
    aula: str = Field(description="Room/classroom")

    class Config:
        arbitrary_types_allowed = True

    def get_codigo(self) -> str:
        """Get the course code (faculty + dependency + materia)"""
        return f"{self.facultad}{self.dependencia}{self.materia}"

    def __repr__(self) -> str:
        return f"Course(id={self.id}, nombre={self.nombre!r}, codigo={self.get_codigo()}, grupo={self.grupo}, tipo={self.tipo!r}, nivel={self.nivel}, horario={self.horario!r}, profesor={self.profesor}, aula={self.aula!r})"


if __name__ == "__main__":
    # Example usage
    course = Course(
        nombre="INFORMÁTICA I",
        facultad=2,
        dependencia=2,
        ide="IIE",
        materia=1,
        grupo=1,
        tipo="T-P",
        es_lab=False,
        nivel=1,
        horas_teoricas=4,
        horas_practicas=3,
        horas_tp=0,
        electiva=False,
        es_dept=True,
        horario="L16-18|M8-10",
        profesor=[123456, 789012],
        aula="A101"
    )
    print(course)
    print(f"Course code: {course.get_codigo()}")