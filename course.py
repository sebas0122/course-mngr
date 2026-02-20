##
# @file course.py
# @brief Course data model using SQLModel ORM
#
# This module defines the Course class which represents the 'materias' (courses) table
# in the database. It uses SQLModel for ORM functionality and provides methods for
# course code generation and string representation.
#
# @author Nelson Parra (nelson.parra@udea.edu.co)
# @date 2025

from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column
from sqlalchemy import ARRAY, Integer


##
# @class Course
# @brief SQLModel representing a university course
#
# This class maps to the 'materias' table in the database and stores all information
# about a course including its code, name, schedule, professors, room assignment,
# and academic details such as semester level and hours.
#
# The class supports courses with multiple professors and provides utility methods
# for generating course codes and formatted representations.
class Course(SQLModel, table=True):
    """
    Course model representing the 'materias' table in the database.
    """
    __tablename__ = "materias"

    id: Optional[int] = Field(default=None, primary_key=True)  ##< Primary key identifier
    nombre: str = Field(description="Course name")  ##< Full name of the course
    facultad: int = Field(description="Faculty code")  ##< Faculty code (e.g., 25 for Engineering)
    dependencia: int = Field(description="Dependency code")  ##< Department/dependency code
    ide: str = Field(description="IDE identifier")  ##< IDE acronym (e.g., IIE)
    materia: int = Field(description="Course/subject code")  ##< Unique course number within department
    grupo: int = Field(description="Group number")  ##< Group/section number for the course
    tipo: str = Field(description="Course type (T-P, etc.)")  ##< Type: T (theory), P (practice), T-P (both)
    es_lab: bool = Field(description="Is laboratory", alias="is_laboratory")  ##< True if this is a laboratory session
    nivel: int = Field(description="Semester/level")  ##< Semester level (1-10, or 21+ for electives)
    horas_teoricas: int = Field(description="Theory hours")  ##< Number of theory hours per week
    horas_practicas: int = Field(description="Practice hours")  ##< Number of practice hours per week
    horas_tp: int = Field(description="TP hours")  ##< Theory-practice combined hours
    electiva: bool = Field(description="Is elective")  ##< True if course is an elective
    es_dept: bool = Field(description="Is department course")  ##< True if course belongs to department
    horario: str = Field(description="Schedule string (e.g., 'L16-18|M8-10')")  ##< Schedule in compact format
    profesor: List[int] = Field(default_factory=list, sa_column=Column(ARRAY(Integer)), description="List of professor IDs")  ##< List of professor identification numbers
    aula: str = Field(description="Room/classroom")  ##< Room or classroom assignment

    class Config:
        arbitrary_types_allowed = True 

    ##
    # @brief Generate the complete course code
    #
    # Constructs a course code by concatenating faculty, dependency, and course numbers.
    # For example, faculty=25, dependency=98, materia=1 produces "25981".
    #
    # @return String containing the concatenated course code
    def get_codigo(self) -> str:
        """Get the course code (faculty + dependency + materia)"""
        return f"{self.facultad}{self.dependencia}{self.materia}"

    ##
    # @brief String representation of the Course object
    #
    # Creates a formatted string showing key course information including ID, name,
    # code, group, type, level, schedule, professors, and room assignment.
    #
    # @return Formatted string representation of the course
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