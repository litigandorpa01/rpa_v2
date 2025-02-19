import time
import asyncio
import logging
import traceback
from datetime import datetime
from app.constants import WEBSITE_URL
from datetime import datetime,timedelta
from app.utils.browser_config import BrowserConfigChrome

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PublicacionesScraper:
    def __init__(self, despa_liti,cod_despacho,ultima_fecha,interval_days):
        self.website_url = WEBSITE_URL
        self.despa_liti = despa_liti
        self.cod_despacho=cod_despacho
        self.ultima_fecha=datetime.strptime(ultima_fecha, "%d/%m/%Y").date()
        self.interval_days=int(interval_days)
        self.driver = None

    async def configure_driver(self):
        """Configura e inicializa el driver de Selenium en un hilo separado."""
        try:
            chrome_options = BrowserConfigChrome.get_chrome_options()
            # Inicializa el driver de Chrome

            self.driver = await asyncio.to_thread(webdriver.Chrome, options=chrome_options)
            
            # Aplica técnicas stealth para ocultar que se está usando Selenium
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True
            )
            
            logging.info("Driver Chrome configurado con Selenium-Stealth")
        except Exception as e:
            logging.info(f"❌ Error al iniciar el driver: {e}")
            raise e
        
    def apply_anti_detection_scripts(self):
        """ Aplica técnicas para evitar la detección de Selenium en la página. """
        try:
            scripts = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                "navigator.permissions.query = (parameters) => Promise.resolve({ state: 'granted' });",
                "window.chrome = { runtime: {} };",
                """
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
                """,
                """
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Open Source Technology Center';
                    if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 620';
                    return WebGLRenderingContext.prototype.getParameter(parameter);
                };
                """,
                "Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });"
            ]

            for script in scripts:
                self.driver.execute_script(script)

            logging.info("✅ Medidas anti-detección aplicadas con éxito.")
        except Exception as e:
            logging.warning(f"⚠️ Error al aplicar medidas anti-detección: {e}")
 
    def get_date_links(self) -> dict:
        """ Extrae las publicaciones y filtra por fecha. """
        try:
            processal_container = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'efectosProcesales')]"))
            )
            li_elements = processal_container.find_elements(By.XPATH, ".//li[@data-qa-id='row']")
            
            data = {}
            for li in li_elements:
                try:
                    publish_date_text = li.find_element(By.XPATH, ".//p[contains(@class, 'publish-date')]").text.strip()
                    str_date = publish_date_text.split(":")[-1].strip()
                    publication_date = datetime.strptime(str_date, "%Y-%m-%d").date()

                    urls = [link.get_attribute("href") for link in li.find_elements(By.XPATH, ".//a") if link.get_attribute("href")]

                    if publication_date in data:
                        data[publication_date].extend(urls)  # Si la fecha ya existe, añade los nuevos links
                    else:
                        data[publication_date] = urls  # Si la fecha no existe, crea la entrada
                    
                except Exception:
                    logging.warning("⚠️ No se encontró fecha en un <li>.")

            fecha_inicio = self.ultima_fecha - timedelta(days=self.interval_days)
            fecha_actual = datetime.today().date()
            
            logging.info(fecha_actual)
            
            data_filtered = {fecha: urls for fecha, urls in data.items() if fecha_inicio <= fecha <= fecha_actual}
            
            print(list(data.keys())) 
            print(list(data_filtered.keys())) 

            return data_filtered
        except Exception as e:
            logging.error(f"❌ Error en `get_date_links`: {e}")
            raise e
    
    async def run(self):
        """Ejecuta el scraper y maneja la interacción con la página web."""
        try:
            await self.configure_driver()
            self.driver.get(f"{self.website_url}{self.cod_despacho}&_co_com_avanti_efectosProcesales_PublicacionesEfectosProcesalesPortlet_INSTANCE_qOzzZevqIWbb_delta=75")
            time.sleep(1.5)
            
            legal_office = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-despacho-container']"))
            )
                
            # if legal_office.text !='Todos':
            #     print("hola")
            # else:

            data_links = self.get_date_links()
            logging.info(f"🔍 {len(data_links)} fechas encontradas.")
             

        
        except Exception as e:
            logging.error("Ocurrió un error durante la ejecución del scraper:")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(f"error_{timestamp}.png")
            logging.error(f"❌ Error durante la ejecución:\n{traceback.format_exc()}")
    
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Driver cerrado.")
