import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Configure the WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
service = ChromeService(ChromeDriverManager().install())

# Monitor function
def monitor_gemini_code_blocks(url):
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    try:
        while True:
            # Locate Gemini code blocks
            code_blocks = driver.find_elements(By.CSS_SELECTOR, 'gemini-code-block-selector')
            for index, block in enumerate(code_blocks):
                code_content = block.text
                save_to_disk(code_content, index)
            time.sleep(10)  # Wait for some time before checking again
    finally:
        driver.quit()

# Save code content to a file
def save_to_disk(content, index):
    file_name = f'gemini_code_block_{index}.txt'
    with open(file_name, 'w') as file:
        file.write(content)
    print(f'Saved: {file_name}')  

# Example usage
# monitor_gemini_code_blocks('http://example.com')
