import os
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent

class BrowserConfig:
    @staticmethod
    def get_firefox_options() -> Options:
        """
        Configura las opciones del navegador Firefox para Selenium con opciones avanzadas.
        
        Retorno:
            Options: Objeto de configuración de Firefox listo para ser usado con Selenium.
        """
        firefox_options = Options()
        ua = UserAgent()

        # 1. Configuración básica
        firefox_options.add_argument("--width=1100")
        firefox_options.add_argument("--height=1000")
        firefox_options.set_preference("general.useragent.override", ua.random)  # User-Agent aleatorio
        firefox_options.set_preference("intl.accept_languages", "en-US")  # Idioma en inglés

        # 2. Evitar detección de Selenium
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("privacy.resistFingerprinting", True)  # Mejora la protección contra huellas digitales

        # 3. Desactivar notificaciones, pop-ups y WebRTC
        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("dom.push.enabled", False)
        firefox_options.set_preference("media.peerconnection.enabled", False)  # Deshabilita WebRTC

        # 4. Mejorar estabilidad
        firefox_options.set_preference("browser.tabs.remote.autostart", False)
        firefox_options.set_preference("browser.tabs.remote.autostart.2", False)

        # 5. Configuración temporal para datos de usuario
        # user_data_dir = tempfile.mkdtemp()
        # firefox_options.set_preference("profile", user_data_dir)

        return firefox_options

    @staticmethod
    def get_geckodriver_path() -> str:
        """
        Retorna la ruta completa del geckodriver almacenado en la carpeta drivers.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "../drivers/geckodriver")
