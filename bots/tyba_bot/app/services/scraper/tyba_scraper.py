import time
import random
import asyncio
import logging
import traceback
from datetime import datetime
from app.utils.browser_config import BrowserConfigChrome
from app.constants import WEBSITE_URL, WEBSITE_KEY, PAGE_ACTION
from app.services.captcha.solver_factory import CaptchaSolverFactory

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TybaScraper:
    def __init__(self, process_id, captcha_type):
        self.website_url = WEBSITE_URL
        self.website_key = WEBSITE_KEY
        self.page_action = PAGE_ACTION
        self.process_id = process_id
        self.captcha_type = captcha_type
        self.driver = None

    async def configure_driver(self):
        """Configura e inicializa el driver de Selenium en un hilo separado."""
        try:
            chrome_options = BrowserConfigChrome.get_chrome_options()
            # Inicializa el driver de Chrome

            self.driver = await asyncio.to_thread(webdriver.Chrome, options=chrome_options)
            
            # Aplica técnicas stealth para ocultar que se está usando Selenium
            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            
            logging.info("Driver Chrome configurado con Selenium-Stealth")
        except Exception as e:
            logging.info(f"❌ Error al iniciar el driver: {e}")
            raise e
    
    async def consult_process(self):
        max_intentos = 10 
        intentos = 0

        while intentos < max_intentos:
            intentos += 1
            logging.info(f"🔄 Intento {intentos} de {max_intentos}")

            try:
                # Encontrar el campo de texto
                text_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='MainContent_txtCodigoProceso']"))
                )
                time.sleep(random.uniform(2, 4))

                # await self.simulate_mouse_movement(text_input)
                text_input.clear()
                text_input.click()

                # Escribir el código de proceso
                text_input.send_keys(self.process_id)

                time.sleep(random.uniform(4, 7))

                # Resolver CAPTCHA
                logging.info("Resolviendo CAPTCHA...")
                solver = CaptchaSolverFactory.get_solver(self.captcha_type)
                captcha_response = await solver.solve(self.website_url, self.website_key, self.page_action)
                logging.info("CAPTCHA resuelto")

                # Inyectar el token CAPTCHA
                self.driver.execute_script(f"""
                    let textarea = document.querySelector("textarea[name='g-recaptcha-response']"); 
                    if (textarea) {{ textarea.value = '{captcha_response}'; }}
                """)

                time.sleep(random.uniform(3, 5))

                # Hacer clic en "Consultar"
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@value='Consultar']"))
                )
                btn.click()
                
                time.sleep(random.uniform(3, 5))

                # Esperar a que aparezca el mensaje de respuesta
                informative_banner = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='MainContent_UC_MensajeInformativo_lblTitulo']"))
                )
                mensaje = informative_banner.text.strip()

                if mensaje == "¡Correcto!":
                    logging.info("✅ Consulta realizada con éxito.")
                    return True  # Sale del bucle y continúa con el flujo principal
                
                logging.warning(f"⚠️ Respuesta inesperada: '{mensaje}'. Reintentando...")

            except Exception as e:
                logging.warning(f"⚠️ No se encontró el mensaje de respuesta o hubo un error: {e}. Reintentando...")

        logging.error("❌ Se alcanzó el número máximo de intentos sin éxito.")
        return False  # Indica que no se logró obtener la respuesta esperada

    async def run(self):
        """Ejecuta el scraper y maneja la interacción con la página web."""
        try:
            await self.configure_driver()
            
            self.driver.get(self.website_url)
            
            # Ocultar el WebDriver con JavaScript adicional
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("navigator.permissions.query = (parameters) => Promise.resolve({ state: 'granted' });")
            self.driver.execute_script("window.chrome = { runtime: {} };")
            
            # Falsificar propiedades del navegador
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });
            """)
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 5))
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
            # Intentar consultar el proceso
            if await self.consult_process():
                logging.info("🎉 Proceso consultado exitosamente. Continuando con el flujo...")
            else:
                logging.error("💥 No se pudo consultar el proceso después de 5 intentos.")
                
    
        except Exception as e:
            logging.error("Ocurrió un error durante la ejecución del scraper:")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(f"{self.process_id}_error_{timestamp}.png")
            traceback.print_exc()
    
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Driver cerrado.")
