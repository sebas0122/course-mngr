##
# @file professor.py
# @brief Professor data model using SQLModel ORM
#
# This module defines the Professor class which represents the 'profesores' (professors)
# table in the database. It includes validation for hiring types and education levels,
# with automatic normalization and validation of input data.
#
# @author Nelson Parra (nelson.parra@udea.edu.co)
# @date 2025

from typing import Optional, ClassVar
from sqlmodel import Field, SQLModel


##
# @class Professor
# @brief SQLModel representing a university professor
#
# This class maps to the 'profesores' table in the database and stores professor
# information including name, identification number, email, employment status,
# hiring type, and education level. The class includes validation logic to ensure
# data integrity for hiring and education fields.
#
# Valid hiring types: NO ESPECIFICADO, OCASIONAL, PLANTA, CÁTEDRA, CÁTEDRA CALENDARIO
# Valid education levels: NO ESPECIFICADO, PREGRADO, MAESTRÍA, DOCTORADO, ESPECIALIZACIÓN
class Professor(SQLModel, table=True):
    """
    Professor model representing the 'profesores' table in the database.
    """
    __tablename__ = "profesores"

    id: Optional[int] = Field(default=None, primary_key=True)  ##< Primary key identifier
    nombre: str = Field(description="Professor name")  ##< Full name of the professor
    identificacion: int = Field(description="ID number", unique=True)  ##< Unique identification number (cédula)
    correo: str = Field(description="Email address")  ##< Email address for contact
    catedra: bool = Field(default=False, description="Is cathedra professor")  ##< True if professor is cathedra type
    contratacion: str = Field(default="NO ESPECIFICADO", description="Hiring type")  ##< Type of employment contract
    formacion: str = Field(default="NO ESPECIFICADO", description="Education level")  ##< Highest education degree obtained

    ##< Valid hiring type values for validation
    VALID_HIRING: ClassVar[set] = {
        "NO ESPECIFICADO",
        "OCASIONAL",
        "PLANTA",
        "CÁTEDRA",
        "CÁTEDRA CALENDARIO"
    }

    ##< Valid education level values for validation
    VALID_EDUCATION: ClassVar[set] = {
        "NO ESPECIFICADO",
        "PREGRADO",
        "MAESTRÍA",
        "DOCTORADO",
        "ESPECIALIZACIÓN"
    }

    class Config:
        arbitrary_types_allowed = True

    ##
    # @brief Constructor with input normalization and validation
    #
    # Initializes a Professor object with automatic data normalization and validation.
    # String fields are trimmed, identification is converted to int, and hiring/education
    # fields are validated against allowed values. Invalid values are replaced with
    # "NO ESPECIFICADO" and a warning is printed.
    #
    # @param **data Keyword arguments for professor attributes
    def __init__(self, **data):
        # Normalize inputs before validation
        if 'nombre' in data:
            data['nombre'] = str(data['nombre']).strip()
        if 'identificacion' in data:
            data['identificacion'] = int(data['identificacion'])
        if 'correo' in data:
            data['correo'] = str(data['correo']).strip()
        if 'catedra' in data:
            data['catedra'] = bool(data['catedra'])
        if 'contratacion' in data:
            data['contratacion'] = str(data['contratacion']).strip().upper()
        if 'formacion' in data:
            data['formacion'] = str(data['formacion']).strip().upper()

        # Validate hiring
        if 'contratacion' in data and data['contratacion'] not in self.VALID_HIRING:
            print(f"WARNING: Invalid hiring type '{data['contratacion']}'. Valid values are: {', '.join(sorted(self.VALID_HIRING))}")
            data['contratacion'] = "NO ESPECIFICADO"

        # Validate education
        if 'formacion' in data and data['formacion'] not in self.VALID_EDUCATION:
            print(f"WARNING: Invalid education level '{data['formacion']}'. Valid values are: {', '.join(sorted(self.VALID_EDUCATION))}")
            data['formacion'] = "NO ESPECIFICADO"

        super().__init__(**data)

    ##
    # @brief String representation of the Professor object
    #
    # Creates a formatted string showing professor information including name,
    # identification, email, cathedra status, hiring type, and education level.
    #
    # @return Formatted string representation of the professor
    def __repr__(self) -> str:
        return f"Professor(nombre={self.nombre!r}, identificacion={self.identificacion!r}, correo={self.correo!r}, catedra={self.catedra!r}, contratacion={self.contratacion!r}, formacion={self.formacion!r})"


if __name__ == "__main__":
    prof = Professor(
        nombre="Dr. John Doe",
        identificacion=123456,
        correo="johndoe@example.com",
        catedra=True,
        contratacion="ocasional",
        formacion="doctorado"
    )
    print(prof)