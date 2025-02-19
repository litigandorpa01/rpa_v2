import time
import random
import asyncio
import logging
import traceback
from datetime import datetime
from app.constants import WEBSITE_URL
from app.utils.browser_config import BrowserConfigChrome

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PublicacionesScraper:
    def __init__(self, despa_liti,cod_despacho,ultima_fecha):
        self.website_url = WEBSITE_URL
        self.despa_liti = despa_liti
        self.cod_despacho=cod_despacho
        self.ultima_fecha=ultima_fecha
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
        
    def scipts_config(self):
        """Aplica una serie de medidas para evitar la detección de Selenium por los sitios web."""
        try:
            # Ocultar WebDriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Falsificar permisos del navegador
            self.driver.execute_script("navigator.permissions.query = (parameters) => Promise.resolve({ state: 'granted' });")
            
            # Simular objeto de Chrome
            self.driver.execute_script("window.chrome = { runtime: {} };")

            # Falsificar propiedades del navegador
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
            """)

            # Falsificar WebGL y Canvas Fingerprinting
            self.driver.execute_script("""
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Open Source Technology Center';
                    if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 620';
                    return WebGLRenderingContext.prototype.getParameter(parameter);
                };
            """)

            # Deshabilitar `navigator.plugins`
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });")

            logging.info("✅ Medidas anti-detección aplicadas con éxito.")
        except Exception as e:
            logging.warning(f"⚠️ Error al aplicar medidas anti-detección: {e}")
    
    async def run(self):
        """Ejecuta el scraper y maneja la interacción con la página web."""
        try:
            await self.configure_driver()

            #Ingresa a pagina
            self.driver.get(f"{self.website_url}{self.cod_despacho}&_co_com_avanti_efectosProcesales_PublicacionesEfectosProcesalesPortlet_INSTANCE_qOzzZevqIWbb_delta=75")
            time.sleep(1.5)
            # self.scipts_config()
            legal_office = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-despacho-container']"))
            )
                
            # if legal_office.text !='Todos':
            #     print("hola")
            # else:

            processal_container = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='efectosProcesales lfr-search-container-wrapper main-content-body']"))
            )
             

                


                    
    
        except Exception as e:
            logging.error("Ocurrió un error durante la ejecución del scraper:")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(f"error_{timestamp}.png")
            traceback.print_exc()
    
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Driver cerrado.")
