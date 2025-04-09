from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

# Configuração do Selenium
options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=options)
driver.get("https://gpsjus.tjrn.jus.br/1grau_gerencial_publico.php")

# Aguarda o carregamento do select
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "unidade")))

data = []

def get_text_safe(xpath, default="N/A", timeout=5):
    """Tenta obter o texto de um elemento pelo XPath, retornando um valor padrão se não for encontrado."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text.strip()
    except:
        return default

# Obtém todas as opções disponíveis no select
select_element = driver.find_element(By.ID, "unidade")
select = Select(select_element)
options = select.options

# Mensagem inicial
console.print("\n[bold cyan]🔍 Iniciando coleta de dados...[/]\n")

# Percorre todas as unidades disponíveis (ignorando a primeira opção "Selecione uma opção")
#for index in track(range(1, 5), description="📊 Coletando dados..."):
for index in track(range(1, len(options)), description="📊 Coletando dados..."):
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "unidade"))
        )
        select = Select(select_element)
        select.select_by_index(index)
        WebDriverWait(driver, 10).until(EC.staleness_of(select_element))
        
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "unidade"))
        )
        select = Select(select_element)
        unidade = select.first_selected_option.text.strip()
        
        acervo = get_text_safe("//h3[text()='Acervo']/following-sibling::div[@class='box-rounded']/a/div[@class='big']")
        processos_parados = get_text_safe("//table[@class='lined']/tfoot/tr/td[last()]/a")
        
        decisoes = get_text_safe("//tr[td/strong[text()='Decisões']]/td[last()]")
        despachos = get_text_safe("//tr[td/strong[text()='Despachos']]/td[last()]")
        julgamentos = get_text_safe("//tr[td/strong[text()='Julgamentos']]/td[last()]")
        
        cojud = get_text_safe("//tr[td[text()='COJUD']]/td[2]")
        inquerito_remetido = get_text_safe("//tr[td[text()='INQUÉRITO REMETIDO AO MP']]/td[2]")
        aguardando_pericia = get_text_safe("//tr[td[text()='Aguardando Perícia, Laudo Técnico ou Outros']]/td[2]")
        
        saldo = get_text_safe("//tfoot/tr/td[last()]")
        saldo_demonstrativo = get_text_safe("//div[@class='title' and text()='Demonstrativo de Distribuições (últimos 12 meses)']/following-sibling::table/tfoot/tr/td[last()]")
        
        baixados = get_text_safe("//div[@class='title'][text()='Processos Baixados* (últimos 12 meses)']/following-sibling::table[@class='styled']/tbody/tr[td[text()='Baixados']]/td[last()]")

        processos_conclusos = get_text_safe("//tr[td[text()='Total de processos conclusos']]/td[last()]")

        data.append([index, unidade, acervo, processos_parados, decisoes, despachos, julgamentos, cojud, inquerito_remetido, aguardando_pericia, saldo, saldo_demonstrativo, baixados, processos_conclusos])
        
        console.print(f"[bold green]✔ Coletado:[/] [cyan]{unidade}[/] - [yellow]Acervo:[/] {acervo} - [magenta]Processos parados:[/] {processos_parados} - [blue]Saldo Demonstrativo:[/] {saldo_demonstrativo} - [dark_cyan]Baixados:[/] {baixados} - [yellow]Processos Conclusos (+100 dias): {processos_conclusos}")
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao processar a unidade {index}: {str(e)}[/]")

driver.quit()

table = Table(title="📊 Resultados da Coleta")
columns = ["ID", "Unidade", "Acervo", "Processos parados", "Decisões", "Despachos", "Julgamentos", "COJUD", "Inquérito Remetido", "Aguardando Perícia", "Saldo", "Saldo de Demonstrativo de Distribuição", "Baixados", "Processos Conclusos"]
for col in columns:
    table.add_column(col, style="bold")
for row in data:
    table.add_row(*[str(item) for item in row])
console.print("\n[bold cyan]📌 Dados Coletados:[/]")
console.print(table)

with open("dados_tjrn.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(columns)
    writer.writerows(data)
console.print("\n[bold magenta]✅ Coleta finalizada. Dados salvos em 'dados_tjrn.csv'.[/]\n")