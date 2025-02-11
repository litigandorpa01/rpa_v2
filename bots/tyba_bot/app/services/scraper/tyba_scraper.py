import time
import asyncio
from app.utils.browser_config import BrowserConfig
from app.services.captcha.solver_factory import CaptchaSolverFactory
from app.constants import WEBSITE_URL,WEBSITE_KEY

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TybaScraper:
    def __init__(self,process_id,captcha_type):
        self.website_url=WEBSITE_URL
        self.website_key=WEBSITE_KEY
        self.process_id=process_id
        self.captcha_type=captcha_type
        self.driver = None

    async def configure_driver(self):
        """Configura e inicializa el driver de Selenium en un hilo separado."""
        firefox_options = BrowserConfig.get_firefox_options()
        self.driver = await asyncio.to_thread(webdriver.Firefox, options=firefox_options)
        print("Driver Firefox configurado")


    async def run(self):
        """Ejecuta el scraper y maneja la interacción con la página web."""
        try:
            await self.configure_driver()
            self.driver.get( self.website_url)

            # Esperar a que el elemento de entrada esté presente
            text_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='MainContent_txtCodigoProceso']"))
            )
            text_input.click()
            text_input.clear()
            text_input.send_keys(self.process_id)

            # Resolver el CAPTCHA v3
            print("Resolviendo CAPTCHA...")
            solver = CaptchaSolverFactory.get_solver(self.captcha_type)
            captcha_response=await solver.solve(self.website_url, self.website_key)
            
            print(f"CAPTCHA resuelto. Token: {captcha_response}")

            # Inyectar el token resuelto en el formulario
            self.driver.execute_script(f"""
                let textarea = document.querySelector("textarea[name='g-recaptcha-response']");
                if (textarea) {{
                    textarea.value = '{captcha_response}';
                }}
            """)

            # Hacer clic en el botón de consulta
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Consultar']"))
            )
            btn.click()

            # Esperar la respuesta del servidor
            WebDriverWait(self.driver, 3).until(
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
