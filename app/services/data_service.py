import json
from pathlib import Path
from typing import List, Dict
from rich.table import Table
from rich.console import Console

console = Console()

class DataService:
    def __init__(self, data_file: str = 'data/dados_tjrn.json'):
        self.data_file = Path(data_file)
        self.data = self.load_data()
    
    def load_data(self) -> List[Dict]:
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self, data: List[Dict]):
        self.data_file.parent.mkdir(exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def display_data_table(self):
        table = Table(title="📊 Resultados da Coleta")
        table.add_column("ID", justify="right")
        table.add_column("Unidade", justify="left")
        table.add_column("Acervo Total", justify="right")
        
        for item in self.data:
            table.add_row(
                str(item["id"]),
                item["unidade"],
                item["acervo_total"]
            )
        
        console.print(table)