import asyncio

from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV3ProxylessRequest


class CaptchaResolver:
    API_KEY = "7572ae3696ef56c6f6cb812283da1c85"

    @staticmethod
    def solve_captcha(website_url, website_key):
        """Resuelve el CAPTCHA v3 utilizando CapMonster Cloud."""
        async def _solve():
            client_options = ClientOptions(api_key=CaptchaResolver.API_KEY)
            cap_monster_client = CapMonsterClient(options=client_options)
            recaptcha_request = RecaptchaV3ProxylessRequest(
                websiteUrl=website_url,
                websiteKey=website_key,
                min_score=0.3
            )
            response = await cap_monster_client.solve_captcha(recaptcha_request)
            return response.get("gRecaptchaResponse", "")

        print("Resolviendo CAPTCHA...")
        return asyncio.run(_solve())
