from fastapi import APIRouter, HTTPException
from app.services.data_service import DataService
from app.models.schemas import UnidadeData
from typing import List

router = APIRouter()
data_service = DataService()

@router.get("/unidades", response_model=List[UnidadeData])
def list_unidades():
    return data_service.data

@router.get("/unidades/{unit_id}", response_model=UnidadeData)
def get_unidade(unit_id: int):
    for unit in data_service.data:
        if unit["id"] == unit_id:
            return unit
    raise HTTPException(status_code=404, detail="Unidade não encontrada")