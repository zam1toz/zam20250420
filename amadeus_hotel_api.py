import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

class HotelSearchTool:
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

    def search_hotels_by_city(self, city_code):
        url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
        headers = {"Authorization": f"Bearer {self.get_amadeus_token()}"}
        params = {"cityCode": city_code}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return []

        return response.json().get("data", [])

    def search_hotel_offers(self, hotel_id, check_in_date, check_out_date, adults=1):
        url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
        headers = {"Authorization": f"Bearer {self.get_amadeus_token()}"}
        params = {
            "hotelIds": hotel_id,
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return None

        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]  # 첫 번째 유효한 오퍼 정보만 반환
        else:
            return None

    def get_available_hotels(self, city_name, check_in_date, check_out_date, adults=1, max_hotels=10):
        city_code = self.get_city_code(city_name)
        city_hotels = self.search_hotels_by_city(city_code)
        available_hotels = []

        for hotel in city_hotels[:max_hotels]:
            hotel_id = hotel["hotelId"]
            hotel_offer = self.search_hotel_offers(hotel_id, check_in_date, check_out_date, adults)

            if hotel_offer:
                hotel_info = {
                    "hotel_name": hotel_offer["hotel"]["name"],
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                    "room_description": hotel_offer["offers"][0]["room"]["description"]["text"],
                    "total_price": hotel_offer["offers"][0]["price"]["total"],
                    "currency": hotel_offer["offers"][0]["price"]["currency"]
                }
                available_hotels.append(hotel_info)

        return available_hotels


if __name__ == "__main__":
    
    hotel_tool = HotelSearchTool()
    hotels = hotel_tool.get_available_hotels('오사카', "2025-04-25", "2025-04-27", adults=1)

    for idx, hotel in enumerate(hotels, start=1):
        print(f"{idx}. {hotel['hotel_name']}")
        print(f"📅 숙박 기간: {hotel['check_in']} ~ {hotel['check_out']}")
        print(f"🛏 객실 정보: {hotel['room_description']}")
        print(f"💳 총 가격: {hotel['total_price']} {hotel['currency']}")
        print("-" * 50)
        
        