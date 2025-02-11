import time
import asyncio
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV3ProxylessRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.browser_config import BrowserConfig

class TybaScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.api_key = "7572ae3696ef56c6f6cb812283da1c85"  # Tu API key de CapMonster

    def configure_driver(self):
        """Configura e inicializa el driver de Selenium."""
        firefox_options = BrowserConfig.get_firefox_options()
        self.driver = webdriver.Firefox(options=firefox_options)
        print("Driver Firefox configurado")

    async def solve_captcha(self, website_url, website_key):
        """Resuelve el CAPTCHA v3 utilizando CapMonster Cloud."""
        client_options = ClientOptions(api_key=self.api_key)
        cap_monster_client = CapMonsterClient(options=client_options)
        recaptcha_request = RecaptchaV3ProxylessRequest(
            websiteUrl=website_url,
            websiteKey=website_key,
            min_score=0.3  # Define el puntaje mínimo aceptable (0.1 a 1.0)
        )
        response = await cap_monster_client.solve_captcha(recaptcha_request)
        return response.get("gRecaptchaResponse", "")

    def run(self):
        """Corre el scraper y maneja la interacción con la página web."""
        try:
            self.configure_driver()
            self.driver.get(self.url)

            # Esperar a que el elemento de entrada esté presente
            text_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='MainContent_txtCodigoProceso']"))
            )
            text_input.click()
            text_input.clear()
            text_input.send_keys("05001418900120240119200")

            # Resolver el CAPTCHA v3
            print("Resolviendo CAPTCHA...")
            captcha_response = asyncio.run(self.solve_captcha(
                website_url=self.url,
                website_key="6Ldf8zAiAAAAAAq1LUwvTCwki5C6uuIg0zVw4of0"
            ))
            print(f"CAPTCHA resuelto. Token: {captcha_response}")

            # Inyectar el token resuelto en el formulario
            self.driver.execute_script(f"""
                let textarea = document.querySelector("textarea[name='g-recaptcha-response']");
                if (textarea) {{
                    textarea.value = '{captcha_response}';
                }}
            """)

            # Verificar si el token se inyectó correctamente
            injected_token = self.driver.execute_script(
                "return document.querySelector('textarea[name=\"g-recaptcha-response\"]').value;"
            )

            # Hacer clic en el botón de consulta
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Consultar']"))
            )
            btn.click()

            # Esperar la respuesta del servidor
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@title='Consultar registro']"))
            )
            print("Consulta realizada con éxito.")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            time.sleep(5)
            if self.driver:
                self.driver.quit()
                print("Driver cerrado.")

if __name__ == "__main__":
    for i in range(1, 6):
        print(f"Ejecutando el scraper - Iteración {i}")
        bot = TybaScraper(
            url="https://procesojudicial.ramajudicial.gov.co/Justicia21/Administracion/Ciudadanos/frmConsulta.aspx"
        )
        bot.run()
        print("Scraper terminado.\n")
