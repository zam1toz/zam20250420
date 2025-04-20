from crew import TravelCoordinatorCrew

def run():
    """
    Run the crew.
    """
    inputs = {
        'content': 
            "2025년 4월 25일부터 27일까지 인천을 출발해서 오사카로 여행을 다녀오려고 합니다. "
            "항공편, 숙소, 현지 맛집, 가볼만한 곳까지 포함해서 여행 일정을 상세히 만들어주세요. "
            "예산은 총 80만 원 이내로 잡고 있어요. "
            "혼자 가는 여행이라 너무 비싸지 않으면서 가성비 좋은 곳들로 부탁드려요."
    }

    
    return TravelCoordinatorCrew().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    result = run()
    print(result)
    
    
    