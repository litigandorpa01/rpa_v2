from app.services.captcha.captcha_resolver import CaptchaSolver,ReCaptchaV3Solver

#Factory
class CaptchaSolverFactory:
    @staticmethod
    def get_solver(captcha_type: str) -> CaptchaSolver:
        if captcha_type == 'recaptcha_v2':
            raise ValueError(f"recaptcha_v2 no soportado: {captcha_type}")
        elif captcha_type == 'recaptcha_v3':
            return ReCaptchaV3Solver()
        elif captcha_type == 'hcaptcha':
           raise ValueError(f"hcaptcha no soportado: {captcha_type}")
        else:
            raise ValueError(f"Tipo de CAPTCHA no soportado: {captcha_type}")