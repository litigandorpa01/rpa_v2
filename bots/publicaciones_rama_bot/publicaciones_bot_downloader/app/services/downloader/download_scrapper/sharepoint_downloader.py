import os

from playwright.async_api import TimeoutError

from app.constants import SHARE_POINT_FOLDER

class Scraper:
    def __init__(self, file_url:str, file_name:str):
        self.file_url = file_url
        self.file_name=file_name
        self.download_dir = SHARE_POINT_FOLDER
        self.browser = None
        self.context = None
        self.page = None

    async def setup_browser(self, playwright):
        """Configura el navegador, contexto y página."""
        try:
            self.browser = await playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context(accept_downloads=True)
            self.page = await self.context.new_page()
        except Exception as e:
            raise RuntimeError(f"Error al configurar el navegador: {e}")

    async def navigate_to_page(self):
        """Navega a la página proporcionada."""
        if self.page.is_closed():
            raise RuntimeError("La página está cerrada, no se puede navegar.")
        try:
            await self.page.goto(self.file_url, timeout=20000)
        except TimeoutError:
            raise TimeoutError("Error: Tiempo de espera agotado al intentar cargar la página.")
        except Exception as e:
            raise RuntimeError(f"Error al navegar a la página: {e}")

    async def wait_for_selector_and_click(self, selector, timeout=10000):
        """Espera a que un selector esté presente y luego hace clic en él."""
        if self.page.is_closed():
            raise RuntimeError("La página está cerrada, no se puede hacer clic.")
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.locator(selector).click()
        except TimeoutError:
            raise TimeoutError(f"Error: Selector '{selector}' no encontrado dentro del tiempo límite.")
        except Exception as e:
            raise RuntimeError(f"Error al hacer clic en el selector: {e}")

    async def handle_download(self):
        """Maneja la descarga del archivo evitando duplicaciones y usando el nombre personalizado con la extensión correcta."""
        if self.page.is_closed():
            raise RuntimeError("La página está cerrada, no se puede manejar la descarga.")
        try:
            async with self.page.expect_download() as download_info:
                await self.page.locator("//button[contains(@data-automationid, 'downloadCommand')]").click()
            
            download = await download_info.value
            
            if self.file_name:
                # Si el nombre no tiene extensión, agregamos la extensión del archivo descargado
                if not os.path.splitext(self.file_name)[1]:
                    # Obtener la extensión del archivo descargado
                    file_extension = os.path.splitext(download.suggested_filename)[1]
                    self.file_name += file_extension
                
                file_path = os.path.join(self.download_dir, self.file_name)


            await download.save_as(file_path)
            return file_path
        
        except Exception as e:
            raise RuntimeError(f"Error durante la descarga: {e}")
        
    async def run_download(self, playwright):
        """Orquestador tareas scraping."""
        try:
            await self.setup_browser(playwright)
            await self.navigate_to_page()
            await self.wait_for_selector_and_click("//div[contains(@data-automationid, 'row-selection-header')]")
            file_path = await self.handle_download()
            return file_path
        except Exception as e:
            print(f"Ocurrió un error durante el scraping: {e}")
        finally:
            if self.browser:
                await self.browser.close()

