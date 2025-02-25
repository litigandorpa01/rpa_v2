import asyncio
import logging
from datetime import datetime, timedelta

from app.constants import WEBSITE_URL
from app.utils.browser_config import BrowserConfigChrome
from app.services.rabbitmq.producer import RabbitMQProducer

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PublicacionesScraper:
    def __init__(self, despa_liti, cod_despacho, ultima_fecha, interval_days):
        self.website_url = WEBSITE_URL
        self.despa_liti = despa_liti
        self.cod_despacho = cod_despacho
        self.ultima_fecha = datetime.strptime(ultima_fecha, "%d/%m/%Y").date()
        self.interval_days = int(interval_days)
        self.driver = None

    async def configure_driver(self):
        """Configura e inicializa el driver de Selenium en un hilo separado."""
        try:
            chrome_options = BrowserConfigChrome.get_chrome_options()
            self.driver = await asyncio.to_thread(webdriver.Chrome, options=chrome_options)

            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True
            )

            logging.info("Driver Chrome configurado correctamente con Selenium-Stealth.")
        except Exception as e:
            logging.error(f"❌ Error al iniciar el driver: {e}")
            raise  # Se escala el error

    def get_external_date_links(self) -> dict:
        """Extrae publicaciones filtrando por fecha."""
        try:
            publication_rows = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'efectosProcesales')]//li[@data-qa-id='row']"))
            )

            data = {}
            for row in publication_rows:
                try:
                    publish_date_text = row.find_element(By.XPATH, ".//p[contains(@class, 'publish-date')]").text.strip()
                    str_date = publish_date_text.split(":")[-1].strip()
                    publication_date = datetime.strptime(str_date, "%Y-%m-%d").date()

                    url_data = []
                    links = row.find_elements(By.XPATH, ".")

                    for link in links:
                        url = link.get_attribute("href")
                        if url:
                            link_text = link.text.strip() or "Sin texto"
                            url_data.append({link_text: url})

                    if publication_date in data:
                        data[publication_date].extend(url_data)
                    else:
                        data[publication_date] = url_data

                except Exception:
                    logging.warning("⚠️ No se encontró fecha en un <li>.")

            fecha_inicio = self.ultima_fecha - timedelta(days=self.interval_days)
            fecha_actual = datetime.today().date()

            data_filtered = {fecha: urls for fecha, urls in data.items() if fecha_inicio <= fecha <= fecha_actual}

            logging.info(f"Fechas extraídas: {len(data_filtered)}")

            return data_filtered
        except Exception as e:
            logging.error(f"❌ Error en `get_external_date_links`: {e}")
            raise  # Se escala el error

    def get_internal_data_links(self, external_data_links: dict) -> dict:
        """Obtiene los enlaces internos de cada publicación."""
        try:
            for key, value_list in external_data_links.items():
                for item in value_list:
                    if isinstance(item, dict) and "VER DETALLE" in item:
                        url_detalle = item['VER DETALLE']
                        self.driver.get(url_detalle)

                        self.driver.execute_script("""
                            let tablaElement = document.querySelector("table[id^='tabla-docs']");
                            if (tablaElement) {
                                let tablaID = "#" + tablaElement.id; 
                                if ($.fn.DataTable.isDataTable(tablaID)) {
                                    let tabla = $(tablaID).DataTable();
                                    tabla.page.len(-1).draw();
                                } 
                            } 
                        """)

                        internal_links = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_all_elements_located((By.XPATH,
                                "//div[contains(normalize-space(@class), 'main-title')]//a |"
                                "//div[contains(normalize-space(@class), 'main-contenido')]//div[contains(normalize-space(@class), 'docs-publicacion')]//a")
                            )
                        )
                        for link in internal_links:
                            url = link.get_attribute("href")
                            if url:
                                link_text = link.text.strip() or "Sin texto"
                                value_list.append({link_text: url})

                        value_list[:] = [d for d in value_list if not any(value in (f"{url_detalle}") for value in d.values())]
                        break

            return external_data_links
        except Exception as e:
            logging.error(f"❌ Error en `get_internal_data_links`: {e}")
            raise  # Se escala el error

    async def clear_links(self, internal_data_links: dict) -> dict:
        """Elimina duplicados en los enlaces extraídos y castea clave fecha a str."""
        cleaned_data = {}

        async def process_key(key, value_list):
            unique_dicts = set(frozenset(d.items()) for d in value_list)
            return key.strftime("%Y-%m-%d"), [dict(fset) for fset in unique_dicts]

        try:
            tasks = [process_key(key, value_list) for key, value_list in internal_data_links.items()]
            results = await asyncio.gather(*tasks)

            for key, cleaned_list in results:
                cleaned_data[key] = cleaned_list

            return cleaned_data
        except Exception as e:
            logging.error(f"❌ Error en `clear_links`: {e}")
            raise  # Se escala el error

    async def run(self):
        """Ejecuta el scraper y maneja la interacción con la página web."""
        try:
            await self.configure_driver()
            self.driver.get(f"{self.website_url}{self.cod_despacho}&_co_com_avanti_efectosProcesales_PublicacionesEfectosProcesalesPortlet_INSTANCE_qOzzZevqIWbb_delta=75")

            # Extraer publicaciones externas
            external_data_links = self.get_external_date_links()

            # Obtener links internos
            internal_data_links = self.get_internal_data_links(external_data_links)

            # Limpiar duplicados y organizar data
            cleaned_data = await self.clear_links(internal_data_links)

            logging.info(f"✅ {len(cleaned_data)}- {self.cod_despacho} fechas procesadas correctamente.")
            
            #Publicar data en bot de descargas
            producer=RabbitMQProducer()
            await producer.connect()
            await producer.publish_message(cleaned_data)
            await producer.close()

        except Exception as e:
            logging.error(f"❌ Error crítico en `run`: {e}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if self.driver:
                self.driver.save_screenshot(f"error_{timestamp}.png")

        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Driver cerrado correctamente.")
