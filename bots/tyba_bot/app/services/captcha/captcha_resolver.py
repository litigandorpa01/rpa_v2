# services/captcha/captcha_solver.py
from abc import ABC, abstractmethod
from app.constants import CAPMONSTER_KEY

from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV3ProxylessRequest

class CaptchaSolver(ABC):
    @abstractmethod
    async def solve(self, website_url, website_key):
        """Método abstracto para resolver un CAPTCHA."""
        pass

#Solucion de ReCaptchaV3
class ReCaptchaV3Solver(CaptchaSolver):
    def __init__(self):
        self.api_key = CAPMONSTER_KEY

    async def solve(self, website_url: str, website_key: str, min_score: float = 0.5) -> str:
        client_options = ClientOptions(api_key=self.api_key)
        cap_monster_client = CapMonsterClient(options=client_options)
        recaptcha_request = RecaptchaV3ProxylessRequest(
            websiteUrl=website_url,
            websiteKey=website_key,
            min_score=min_score,
        )
        response = await cap_monster_client.solve_captcha(recaptcha_request)
        return response.get("gRecaptchaResponse", "")
    
