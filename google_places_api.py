import requests
import os
from dotenv import load_dotenv

load_dotenv()

class NearbyPlacesTool:

    # 장소명으로 위치(위도·경도) 얻기
    def get_location_by_name(self, place_name):
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

    # 근처 맛집 찾기 함수
    def find_nearby_restaurants(self, lat, lng, radius=1000):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "restaurant",
            "language": "ko",
            "key": os.getenv("GOOGLE_API_KEY")
        }
        response = requests.get(url, params=params).json()

        if response["status"] != "OK":
            raise Exception(f"근처 맛집 검색 실패: {response['status']}")

        restaurants = [{
            "이름": place["name"],
            "평점": place.get("rating", "정보 없음"),
            "주소": place.get("vicinity"),
            "place_id": place["place_id"]
        } for place in response["results"]]

        return restaurants

    # 맛집 세부정보 얻기 함수
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

        return response["result"]


if __name__ == "__main__":

    nearby_places_tool = NearbyPlacesTool()
    # 사용 예시
    place_name = "웨스틴 오사카 호텔"
    lat, lng = nearby_places_tool.get_location_by_name(place_name)
    print(f"{place_name}의 위치: {lat}, {lng}")

    restaurants = nearby_places_tool.find_nearby_restaurants(lat, lng)

    print("\n🍽️ 근처 맛집 목록:")
    for idx, restaurant in enumerate(restaurants, 1):
        print(f"{idx}. {restaurant['이름']} (평점: {restaurant['평점']}) - 주소: {restaurant['주소']}")

        details = nearby_places_tool.get_place_details(restaurant["place_id"])
        print(f"\n\t📋 '{details['name']}' 세부 정보:")
        print(f"\t주소: {details.get('formatted_address', '정보 없음')}")
        print(f"\t전화번호: {details.get('formatted_phone_number', '정보 없음')}")
        print(f"\t웹사이트: {details.get('website', '정보 없음')}")
        print(f"\t영업시간: {details.get('opening_hours', {}).get('weekday_text', '정보 없음')}")
        print(f"\t평점: {details.get('rating', '정보 없음')}")

        # 리뷰 (옵션)
        reviews = details.get('reviews', [])
        if reviews:
            print("\n\t💬 최근 리뷰:")
            for review in reviews[:3]:  # 최대 3개 리뷰 출력
                print(f"\t- {review['text']} (평점: {review['rating']})")
        
        print("\n------------------------------------------------------------\n")


