from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResultadoCarga:
    """Cuántas filas insertó o actualizó una carga y cuántas venían iguales."""

    insertados: int = 0
    actualizados: int = 0
    sin_cambios: int = 0

    @property
    def total(self) -> int:
        return self.insertados + self.actualizados + self.sin_cambios

    def __add__(self, otro: ResultadoCarga) -> ResultadoCarga:
        return ResultadoCarga(
            self.insertados + otro.insertados,
            self.actualizados + otro.actualizados,
            self.sin_cambios + otro.sin_cambios,
        )

    def como_dict(self) -> dict[str, int]:
        return {
            "insertados": self.insertados,
            "actualizados": self.actualizados,
            "sin_cambios": self.sin_cambios,
        }
