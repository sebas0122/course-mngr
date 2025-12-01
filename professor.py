from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Professor:
    """
    Simple Professor model with basic contact info.
    """
    name: str
    id_number: int
    email: str
    cathedra: bool = False
    hiring: str = "NO ESPECIFICADO"
    education: str = "NO ESPECIFICADO"

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

    def __post_init__(self):
        # normalize inputs
        self.name = str(self.name).strip()
        self.id_number = int(self.id_number)
        self.email = str(self.email).strip()
        self.cathedra = bool(self.cathedra)
        self.hiring = str(self.hiring).strip().upper()
        self.education = str(self.education).strip().upper()

        # Validate hiring
        if self.hiring not in self.VALID_HIRING:
            print(f"WARNING: Invalid hiring type '{self.hiring}'. Valid values are: {', '.join(sorted(self.VALID_HIRING))}")
            self.hiring = "NO ESPECIFICADO"

        # Validate education
        if self.education not in self.VALID_EDUCATION:
            print(f"WARNING: Invalid education level '{self.education}'. Valid values are: {', '.join(sorted(self.VALID_EDUCATION))}")
            self.education = "NO ESPECIFICADO"

    def __repr__(self) -> str:
        return f"Professor(name={self.name!r}, id_number={self.id_number!r}, email={self.email!r}, cathedra={self.cathedra!r}, hiring={self.hiring!r}, education={self.education!r})"


if __name__ == "__main__":
    prof = Professor(
        name="Dr. John Doe",
        id_number=123456,
        email="johndoe@example.com",
        cathedra=True,
        hiring="ocasional",
        education="doctorado"
    )
    print(prof)