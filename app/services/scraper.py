from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.progress import track
import json

console = Console()

class TJRNScraper:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.base_url = "https://gpsjus.tjrn.jus.br/1grau_gerencial_publico.php"
    
    def fetch_data(self, max_units=None):
        self.driver.get(self.base_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "unidade"))
        )
        
        select_element = self.driver.find_element(By.ID, "unidade")
        select = Select(select_element)
        options = select.options
        
        data = []
        max_range = len(options) if max_units is None else min(max_units + 1, len(options))
        
        for index in track(range(1, max_range), description="📊 Coletando dados..."):
            try:
                unit_data = self._process_unit(index, select_element)
                if unit_data:
                    data.append(unit_data)
            except Exception as e:
                console.print(f"[bold red]❌ Erro ao processar a unidade {index}: {str(e)}[/]")
        
        self.driver.quit()
        return data
    
    def _process_unit(self, index, select_element):
        select = Select(select_element)
        select.select_by_index(index)
        WebDriverWait(self.driver, 10).until(EC.staleness_of(select_element))
        
        select_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "unidade"))
        )
        select = Select(select_element)
        unidade = select.first_selected_option.text.strip()
        
        acervo = self._get_acervo()
        processos = self._get_processos_em_tramitacao()
        
        console.print(f"[bold green]✔ Coletado:[/] [cyan]{unidade}[/] - [yellow]Acervo:[/] {acervo}")
        
        return {
            "id": index,
            "unidade": unidade,
            "acervo_total": acervo,
            "processos_em_tramitacao": processos
        }
    
    def _get_acervo(self):
        try:
            acervo_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                "//h3[text()='Acervo']/following-sibling::div[@class='box-rounded']/a/div[@class='big']"))
            )
            return acervo_element.text.strip()
        except:
            return "N/A"
    
    def _get_processos_em_tramitacao(self):
        processos = {
            "CONHECIMENTO": {},
            "EXECUÇÃO": {},
            "EXECUÇÃO FISCAL": {},
            "EXECUÇÃO CRIMINAL": {},
            "TOTAL": {}
        }
        
        try:
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                "//h4[contains(text(), 'Processos em tramitação')]/following::table[1]"))
            )
            
            rows = table.find_elements(By.TAG_NAME, "tr")
            current_category = None
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) == 4:
                    category = cells[0].text.strip()
                    
                    if "CONHECIMENTO" in category:
                        current_category = "CONHECIMENTO"
                        processos[current_category] = self._parse_processos_data(cells)
                        processos[current_category]["Não julgados"] = {}
                    elif "EXECUÇÃO" in category and "FISCAL" not in category and "CRIMINAL" not in category:
                        current_category = "EXECUÇÃO"
                        processos[current_category] = self._parse_processos_data(cells)
                    elif "EXECUÇÃO FISCAL" in category:
                        current_category = "EXECUÇÃO FISCAL"
                        processos[current_category] = self._parse_processos_data(cells)
                        processos[current_category]["Não julgados"] = {}
                    elif "EXECUÇÃO CRIMINAL" in category:
                        current_category = "EXECUÇÃO CRIMINAL"
                        processos[current_category] = self._parse_processos_data(cells)
                    elif "TOTAL" in category:
                        processos["TOTAL"] = self._parse_processos_data(cells)
                    elif "Não julgados" in category:
                        if current_category in ["CONHECIMENTO", "EXECUÇÃO FISCAL"]:
                            processos[current_category]["Não julgados"] = self._parse_processos_data(cells)
        
        except Exception as e:
            console.print(f"[bold yellow]⚠ Aviso:[/] Não foi possível coletar dados de 'Processos em tramitação'. Erro: {str(e)}")
        
        return processos
    
    def _parse_processos_data(self, cells):
        return {
            "Total": cells[1].text.strip(),
            "+60 dias": cells[2].text.strip(),
            "+100 dias": cells[3].text.strip()
        }
    
    def save_to_json(self, data, filename='dados_tjrn.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        console.print(f"\n[bold magenta]✅ Dados salvos em '{filename}'.[/]\n")