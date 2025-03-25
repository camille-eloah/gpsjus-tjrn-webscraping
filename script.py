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

# Obtém todas as opções disponíveis no select
select_element = driver.find_element(By.ID, "unidade")
select = Select(select_element)
options = select.options

# Mensagem inicial
console.print("\n[bold cyan]🔍 Iniciando coleta de dados...[/]\n")

# Percorre todas as unidades disponíveis (ignorando a primeira opção "Selecione uma opção")
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
        
        acervo = "N/A"
        try:
            acervo_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[text()='Acervo']/following-sibling::div[@class='box-rounded']/a/div[@class='big']"))
            )
            acervo = acervo_element.text.strip()
        except:
            pass
        
        processos_parados = "N/A"
        try:
            processos_parados_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@class='lined']/tfoot/tr/td[last()]/a"))
            )
            processos_parados = processos_parados_element.text.strip()
        except:
            pass
        
        decisoes = despachos = julgamentos = "N/A"
        try:
            title_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='title' and text()='Atos judiciais proferidos (últimos 12 meses)']"))
            )
            tabela_element = title_element.find_element(By.XPATH, "following-sibling::table")
            
            try:
                decisoes = tabela_element.find_element(By.XPATH, ".//tr[td/strong[text()='Decisões']]/td[last()]").text.strip()
            except:
                pass
            try:
                despachos = tabela_element.find_element(By.XPATH, ".//tr[td/strong[text()='Despachos']]/td[last()]").text.strip()
            except:
                pass
            try:
                julgamentos = tabela_element.find_element(By.XPATH, ".//tr[td/strong[text()='Julgamentos']]/td[last()]").text.strip()
            except:
                pass
        except:
            console.print(f"[bold yellow]⚠️  Tabela 'Atos Judiciais Proferidos' não encontrada para {unidade}.[/]")
        
        cojud = inquerito_remetido = aguardando_pericia = "N/A"
        try:
            title_element_diligencias = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='title' and contains(text(), 'Controle de Diligências (PJe)')]"))
            )
            tabela_diligencias_element = title_element_diligencias.find_element(By.XPATH, "following-sibling::table")
            
            try:
                aguardando_pericia = tabela_diligencias_element.find_element(By.XPATH, ".//tr[td[text()='Aguardando Perícia, Laudo Técnico ou Outros']]/td[2]").text.strip()
            except:
                pass
            try:
                cojud = tabela_diligencias_element.find_element(By.XPATH, ".//tr[td[text()='COJUD']]/td[2]").text.strip()
            except:
                pass
            try:
                inquerito_remetido = tabela_diligencias_element.find_element(By.XPATH, ".//tr[td[text()='INQUÉRITO REMETIDO AO MP']]/td[2]").text.strip()
            except:
                pass
        except:
            console.print(f"[bold yellow]⚠️  Tabela 'Controle de Diligências (PJe)' não encontrada para {unidade}.[/]")
        
        saldo = "N/A"
        try:
            title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='title' and text()='Demonstrativo de Distribuições (últimos 12 meses)']"))
            )
            tabela_element = title_element.find_element(By.XPATH, "following-sibling::table")
            saldo = tabela_element.find_element(By.XPATH, ".//tfoot/tr/td[last()]").text.strip()
        except:
            pass
        
        data.append([index, unidade, acervo, processos_parados, decisoes, despachos, julgamentos, cojud, inquerito_remetido, aguardando_pericia, saldo])
        
        console.print(f"[bold green]✔ Coletado:[/] [cyan]{unidade}[/] - [yellow]Acervo:[/] {acervo} - [magenta]Processos parados:[/] {processos_parados}")
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao processar a unidade {index}: {str(e)}[/]")

driver.quit()

table = Table(title="📊 Resultados da Coleta")
columns = ["ID", "Unidade", "Acervo", "Processos parados", "Decisões", "Despachos", "Julgamentos", "COJUD", "Inquérito Remetido", "Aguardando Perícia", "Saldo"]
for col in columns:
    table.add_column(col, style="bold")
for row in data:
    table.add_row(*[str(item) for item in row])
console.print("\n[bold cyan]📌 Dados Coletados:[/]")
console.print(table)

with open("dados_tjrn4.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(columns)
    writer.writerows(data)
console.print("\n[bold magenta]✅ Coleta finalizada. Dados salvos em 'dados_tjrn4.csv'.[/]\n")
