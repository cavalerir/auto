"""
Script de Automação - Gemini Code Block Extractor
Monitora a interface do Gemini no navegador e salva blocos de código automaticamente.
"""

import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurações
GEMINI_URL = "https://gemini.google.com"
CHECK_INTERVAL = 5  # segundos
BASE_OUTPUT_DIR = "./gemini_code_blocks"

# Cache para rastrear blocos já processados
processed_blocks = {}

def setup_driver():
    """Configura e retorna o driver do Selenium com Chrome."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Descomente para modo headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_code_blocks(driver):
    """Extrai todos os blocos de código da página."""
    try:
        # Tenta diferentes seletores comuns para blocos de código
        code_blocks = driver.find_elements(By.TAG_NAME, "code")
        
        # Se não encontrar, tenta outros seletores
        if not code_blocks:
            code_blocks = driver.find_elements(By.CLASS_NAME, "code-block")
        
        if not code_blocks:
            code_blocks = driver.find_elements(By.XPATH, "//pre")
        
        return code_blocks
    except NoSuchElementException:
        return []


def parse_code_block(code_text):
    """
    Analisa um bloco de código e extrai o caminho (primeira linha comentada).
    
    Retorna:
        tuple: (file_path, content) ou (None, None) se não houver caminho válido
    """
    lines = code_text.strip().split('\n')
    
    if not lines:
        return None, None
    
    first_line = lines[0].strip()
    
    # Verifica se a primeira linha é um comentário com caminho
    # Suporta // (JavaScript/Go/C++) e # (Python/Shell)
    path_match = re.match(r'^(//|#)\s*(.+)$', first_line)
    
    if not path_match:
        return None, None
    
    file_path = path_match.group(2).strip()
    
    # Remove caracteres inválidos do caminho
    file_path = re.sub(r'[<>:"|?*]', '', file_path)
    
    if not file_path:
        return None, None
    
    # Conteúdo sem a primeira linha (comentário do caminho)
    content = '\n'.join(lines[1:]).strip()
    
    return file_path, content


def save_code_block(file_path, content):
    """
    Salva o bloco de código no disco.
    
    Args:
        file_path: Caminho relativo do arquivo
        content: Conteúdo do código
    
    Retorna:
        bool: True se salvo com sucesso, False caso contrário
    """
    try:
        # Combina com diretório base
        full_path = os.path.join(BASE_OUTPUT_DIR, file_path)
        
        # Cria diretórios se não existirem
        directory = os.path.dirname(full_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # Salva o arquivo
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao salvar '{file_path}': {e}")
        return False


def generate_block_hash(content):
    """Gera um hash para rastrear blocos duplicados."""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()


def process_code_blocks(driver):
    """Processa todos os blocos de código da página."""
    code_blocks = extract_code_blocks(driver)
    
    for idx, block in enumerate(code_blocks):
        try:
            code_text = block.text
            
            if not code_text.strip():
                continue
            
            file_path, content = parse_code_block(code_text)
            
            if not file_path or not content:
                continue
            
            # Gera hash do bloco para evitar duplicidade
            block_hash = generate_block_hash(content)
            
            # Verifica se o bloco já foi processado
            if file_path in processed_blocks and processed_blocks[file_path] == block_hash:
                continue
            
            # Salva o bloco
            if save_code_block(file_path, content):
                print(f"[OK] Arquivo '{file_path}' atualizado com sucesso.")
                processed_blocks[file_path] = block_hash
        
        except Exception as e:
            print(f"[AVISO] Erro ao processar bloco {idx}: {e}")
            continue


def main():
    """Função principal."""
    print(f"Iniciando monitor Gemini Code Extractor...")
    print(f"URL: {GEMINI_URL}")
    print(f"Diretório de saída: {BASE_OUTPUT_DIR}")
    print(f"Intervalo de verificação: {CHECK_INTERVAL}s")
    print("-" * 60)
    
    driver = setup_driver()
    
    try:
        # Abre o site do Gemini
        print("Abrindo Gemini...")
        driver.get(GEMINI_URL)
        
        # Aguarda o carregamento da página
        time.sleep(3)
        
        print("Página carregada. Iniciando monitoramento...")
        print("-" * 60)
        
        # Loop principal
        while True:
            try:
                process_code_blocks(driver)
            except Exception as e:
                print(f"[AVISO] Erro no ciclo de processamento: {e}")
            
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n" + "-" * 60)
        print("Monitoramento interrompido pelo usuário.")
    
    except Exception as e:
        print(f"[ERRO] Erro fatal: {e}")
    
    finally:
        driver.quit()
        print("Driver fechado. Encerrando script.")


if __name__ == "__main__":
    main()