import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ExchangeRateTool():

    def exchange_currency(self, from_currency: str, to_currency: str, amount: float):
        api_key = os.getenv('EXCHANGE_RATE_API_KEY')
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("환율 정보 조회 실패", response.text)

        data = response.json()

        if data['result'] != "success":
            raise Exception("환율 조회에 실패했습니다", data.get('error-type', 'unknown error'))

        converted_amount = data['conversion_result']

        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "original_amount": amount,
            "converted_amount": converted_amount,
            "conversion_rate": data["conversion_rate"]
        }

# 사용 예시
if __name__ == "__main__":
    exchange_tool = ExchangeRateTool()

    result = exchange_tool.exchange_currency(from_currency="USD", to_currency="KRW", amount=100)

    print(f"{result['original_amount']} {result['from_currency']}는 {result['converted_amount']} {result['to_currency']}입니다.")
    print(f"적용된 환율: {result['conversion_rate']}")
    
    