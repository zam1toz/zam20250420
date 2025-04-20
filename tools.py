import time
from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field, PrivateAttr
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# FlightSearchTool
class FlightSearchInput(BaseModel):
    origin_city: str = Field(..., description="출발 도시명(한글), 예: '인천'")
    destination_city: str = Field(..., description="도착 도시명(한글), 예: '오사카'")
    departure_date: str = Field(..., description="출발일자(YYYY-MM-DD)")
    adults: int = Field(1, description="성인 탑승객 수")


class FlightSearchTool(BaseTool):
    name: str = "항공편 검색 도구"
    description: str = "도시명과 날짜를 입력하면 해당 날짜의 항공편을 조회합니다."
    args_schema: Type[BaseModel] = FlightSearchInput

    _amadeus_token: dict = {"access_token": None, "expires_at": 0}

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

    def _run(self, origin_city: str, destination_city: str, departure_date: str, adults: int = 1):
        origin_code = self.get_city_code(origin_city)
        destination_code = self.get_city_code(destination_city)

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


# HotelSearchTool
class HotelSearchInput(BaseModel):
    city_name: str = Field(..., description="숙소를 찾을 도시 이름(예: 오사카, 서울 등)")
    check_in_date: str = Field(..., description="체크인 날짜(YYYY-MM-DD)")
    check_out_date: str = Field(..., description="체크아웃 날짜(YYYY-MM-DD)")
    adults: int = Field(1, description="성인 인원 수")

class HotelSearchTool(BaseTool):
    name: str = "숙소 검색 도구"
    description: str = "도시 이름과 숙박 일정으로 숙박 가능한 호텔 목록과 가격 정보를 조회합니다."
    args_schema: Type[BaseModel] = HotelSearchInput

    _amadeus_token: Dict[str, any] = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._amadeus_token = {"access_token": None, "expires_at": 0}

    def get_amadeus_token(self):
        if self._amadeus_token["access_token"] and time.time() < self._amadeus_token["expires_at"]:
            return self._amadeus_token["access_token"]

        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        response = requests.post(url, data={
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AMADEUS_CLIENT_ID'),
            'client_secret': os.getenv('AMADEUS_CLIENT_SECRET')
        })

        if response.status_code != 200:
            raise Exception("Amadeus 토큰 발급 실패", response.text)

        token_data = response.json()
        self._amadeus_token["access_token"] = token_data["access_token"]
        self._amadeus_token["expires_at"] = time.time() + token_data["expires_in"] - 60

        return self._amadeus_token["access_token"]

    def get_city_code(self, city_name):
        city_codes = {
            "서울": "SEL", "부산": "PUS", "제주": "CJU", "인천": "ICN", "대구": "TAE",
            "오사카": "OSA", "도쿄": "TYO", "후쿠오카": "FUK", "삿포로": "SPK", "교토": "UKY",
            "홍콩": "HKG", "타이베이": "TPE", "방콕": "BKK", "싱가포르": "SIN",
            "하노이": "HAN", "호치민": "SGN", "다낭": "DAD"
        }

        code = city_codes.get(city_name)
        if not code:
            raise ValueError(f"'{city_name}'의 도시 코드를 찾을 수 없습니다.")

        return code

    def search_hotels_by_city(self, city_code):
        url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
        headers = {"Authorization": f"Bearer {self.get_amadeus_token()}"}
        response = requests.get(url, headers=headers, params={"cityCode": city_code})

        if response.status_code != 200:
            return []

        return response.json().get("data", [])

    def search_hotel_offers(self, hotel_id, check_in_date, check_out_date, adults=1):
        url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
        headers = {"Authorization": f"Bearer {self.get_amadeus_token()}"}
        response = requests.get(url, headers=headers, params={
            "hotelIds": hotel_id,
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults
        })

        if response.status_code != 200:
            return None

        data = response.json()
        if "data" in data and data["data"]:
            return data["data"][0]
        return None

    def _run(self, city_name: str, check_in_date: str, check_out_date: str, adults: int = 1, max_hotels: int = 10):
        city_code = self.get_city_code(city_name)
        city_hotels = self.search_hotels_by_city(city_code)
        available_hotels = []

        for hotel in city_hotels[:max_hotels]:
            hotel_offer = self.search_hotel_offers(hotel["hotelId"], check_in_date, check_out_date, adults)
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


# NearbyPlacesTool
class NearbyPlacesInput(BaseModel):
    place_name: str = Field(..., description="검색하고자 하는 장소명")
    radius: int = Field(1000, description="검색 반경(미터 단위)")

class NearbyPlacesTool(BaseTool):
    name: str = "인근 장소 검색 도구"
    description: str = "특정 장소명으로 인근의 가볼 만한 곳들(관광지, 맛집 등)의 상세 정보를 추천합니다."
    args_schema: Type[BaseModel] = NearbyPlacesInput

    def _run(self, place_name: str, radius: int = 1000) -> List[dict]:
        location = self.get_location_by_name(place_name)
        nearby_places = self.find_nearby_places(location, radius)
        detailed_places = [self.get_place_details(place["place_id"]) for place in nearby_places]
        return detailed_places

    def get_location_by_name(self, place_name: str):
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": place_name,
            "language": "ko",
            "key": os.getenv("GOOGLE_API_KEY")
        }
        response = requests.get(url, params=params).json()

        if response["status"] != "OK":
            raise Exception(f"장소 검색 실패: {response['status']}")

        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]

    def find_nearby_places(self, location, radius):
        lat, lng = location
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "tourist_attraction",
            "language": "ko",
            "key": os.getenv("GOOGLE_API_KEY")
        }
        response = requests.get(url, params=params).json()

        if response["status"] != "OK":
            raise Exception(f"주변 장소 검색 실패: {response['status']}")

        return response["results"][:5]  # 최대 5개의 추천장소

    def get_place_details(self, place_id):
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "language": "ko",
            "fields": "name,rating,formatted_address,formatted_phone_number,opening_hours,website,reviews",
            "key": os.getenv("GOOGLE_API_KEY")
        }
        response = requests.get(url, params=params).json()

        if response["status"] != "OK":
            raise Exception(f"세부 정보 조회 실패: {response['status']}")

        result = response["result"]

        return {
            "이름": result.get("name"),
            "주소": result.get("formatted_address"),
            "전화번호": result.get("formatted_phone_number", "정보 없음"),
            "웹사이트": result.get("website", "정보 없음"),
            "영업시간": result.get("opening_hours", {}).get("weekday_text", "정보 없음"),
            "평점": result.get("rating", "정보 없음"),
            "리뷰": [{
                "내용": review.get("text"),
                "평점": review.get("rating")
            } for review in result.get("reviews", [])[:3]]  # 최대 3개 리뷰
        }


# ExchangeRateTool
class ExchangeRateInput(BaseModel):
    from_currency: str = Field(..., description="원본 통화의 코드 (예: USD)")
    to_currency: str = Field(..., description="변환할 대상 통화의 코드 (예: KRW)")
    amount: float = Field(..., description="변환할 금액")

class ExchangeRateTool(BaseTool):
    name: str = "환율 도구"
    description: str = "특정 금액을 한 통화에서 다른 통화로 변환하는 툴입니다."
    args_schema: type[BaseModel] = ExchangeRateInput

    def _run(self, from_currency: str, to_currency: str, amount: float):
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
        
        