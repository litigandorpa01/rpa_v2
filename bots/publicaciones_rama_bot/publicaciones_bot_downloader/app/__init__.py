import logging

logging.basicConfig(
    level=logging.INFO,  # Cambia a DEBUG si quieres más detalles
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Solo muestra logs en la consola
    ]
)

logger = logging.getLogger(__name__)
