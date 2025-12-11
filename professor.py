from typing import Optional, ClassVar
from sqlmodel import Field, SQLModel


class Professor(SQLModel, table=True):
    """
    Professor model representing the 'profesores' table in the database.
    """
    __tablename__ = "profesores"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(description="Professor name")
    identificacion: int = Field(description="ID number", unique=True)
    correo: str = Field(description="Email address")
    catedra: bool = Field(default=False, description="Is cathedra professor")
    contratacion: str = Field(default="NO ESPECIFICADO", description="Hiring type")
    formacion: str = Field(default="NO ESPECIFICADO", description="Education level")

    # Class-level constants for valid values
    VALID_HIRING: ClassVar[set] = {
        "NO ESPECIFICADO",
        "OCASIONAL",
        "PLANTA",
        "CÁTEDRA",
        "CÁTEDRA CALENDARIO"
    }

    VALID_EDUCATION: ClassVar[set] = {
        "NO ESPECIFICADO",
        "PREGRADO",
        "MAESTRÍA",
        "DOCTORADO",
        "ESPECIALIZACIÓN"
    }

    class Config:
        arbitrary_types_allowed = True

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