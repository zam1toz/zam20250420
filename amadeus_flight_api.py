import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

class AirlineSearchTool:
    def __init__(self):
        self._amadeus_token = {
            "access_token": None,
            "expires_at": 0
        }

    def get_amadeus_token(self):
        if self._amadeus_token["access_token"] and time.time() < self._amadeus_token["expires_at"]:
            return self._amadeus_token["access_token"]

        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AMADEUS_CLIENT_ID'),
            'client_secret': os.getenv('AMADEUS_CLIENT_SECRET')
        }

        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception("Amadeus 토큰 발급 실패", response.text)

        token_data = response.json()
        self._amadeus_token["access_token"] = token_data["access_token"]
        self._amadeus_token["expires_at"] = time.time() + token_data["expires_in"] - 60

        return self._amadeus_token["access_token"]

    def get_city_code(self, city_name):
        city_codes = {
            "서울": "SEL", "부산": "PUS", "제주": "CJU", "대구": "TAE", "인천": "ICN",
            "오사카": "OSA", "도쿄": "TYO", "후쿠오카": "FUK", "삿포로": "SPK", "나고야": "NGO",
            "오키나와": "OKA", "교토": "UKY", "요코하마": "YOK", "히로시마": "HIJ",
            "베이징": "BJS", "상하이": "SHA", "광저우": "CAN", "선전": "SZX", "칭다오": "TAO",
            "홍콩": "HKG", "마카오": "MFM", "시안": "SIA",
            "타이베이": "TPE", "가오슝": "KHH",
            "방콕": "BKK", "푸켓": "HKT", "치앙마이": "CNX",
            "하노이": "HAN", "호치민": "SGN", "다낭": "DAD", "나트랑": "NHA",
            "마닐라": "MNL", "세부": "CEB", "보라카이": "MPH",
            "싱가포르": "SIN",
            "쿠알라룸푸르": "KUL", "코타키나발루": "BKI", "페낭": "PEN",
            "자카르타": "JKT", "발리": "DPS", "족자카르타": "JOG",
            "델리": "DEL", "뭄바이": "BOM", "방갈로르": "BLR"
        }

        code = city_codes.get(city_name)
        if not code:
            raise ValueError(f"'{city_name}'의 도시 코드를 찾을 수 없습니다.")
        return code

    def search_flights(self, origin_code, destination_code, departure_date, adults=1):
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {self.get_amadeus_token()}"}
        params = {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": "KRW",
            "max": 10
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception("항공편 조회 실패", response.text)

        flight_data = response.json()
        if "data" not in flight_data or len(flight_data["data"]) == 0:
            return []

        flights = []
        for offer in flight_data["data"]:
            flight_info = {
                "가격": offer["price"]["total"],
                "통화": offer["price"]["currency"],
                "출발지": origin_code,
                "목적지": destination_code,
                "출발일": departure_date,
                "항공사": offer["itineraries"][0]["segments"][0]["carrierCode"],
                "편명": offer["itineraries"][0]["segments"][0]["number"],
                "출발시간": offer["itineraries"][0]["segments"][0]["departure"]["at"],
                "도착시간": offer["itineraries"][0]["segments"][-1]["arrival"]["at"]
            }
            flights.append(flight_info)

        return flights


# 사용 예시
if __name__ == "__main__":
    airline_tool = AirlineSearchTool()
    flights = airline_tool.search_flights("ICN", "OSA", "2025-04-25", adults=1)

    for idx, flight in enumerate(flights, 1):
        print(f"{idx}. 항공사: {flight['항공사']}, 편명: {flight['편명']}, 출발시간: {flight['출발시간']}, 도착시간: {flight['도착시간']}, 가격: {flight['가격']} {flight['통화']}")
        
        