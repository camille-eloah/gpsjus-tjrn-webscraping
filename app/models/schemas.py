from pydantic import BaseModel
from typing import Dict, Optional

class ProcessosTramitacao(BaseModel):
    Total: str
    "+60 dias": str
    "+100 dias": str
    "Não julgados": Optional[Dict[str, str]] = None

class UnidadeData(BaseModel):
    id: int
    unidade: str
    acervo_total: str
    processos_em_tramitacao: Dict[str, ProcessosTramitacao]