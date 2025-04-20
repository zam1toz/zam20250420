from crewai import Task
from agents import coordinator_agent, travel_info_agent, local_recommendation_agent


# 1단계: 기본 여행 정보 작성 (travel_info_agent)
initial_travel_plan_task = Task(
    description=
        "다음 고객의 요청을 바탕으로 항공편(왕복), 숙소를 포함한 여행 일정을 작성합니다. "
        "요청: {content}",
    expected_output="한국어로 작성된 일자별 기본 여행 일정과 비용 초안 (항공편(왕복), 숙소 포함)",
    agent=travel_info_agent,
)

# 2단계: 현지 추천 정보 및 예산 추가 (local_recommendation_agent)
local_recommendation_task = Task(
    description=(
        "1단계에서 작성된 일자별 기본 여행 일정과 비용을 검토한 후, "
        "여행 일정에서 아침/점심/저녁 식사와 간식으로 즐길 수 있는 "
        "현지에서 인기있는 맛집과 메뉴를 추가하고(가격 포함), 가볼만한 명소를 추천합니다.(비용 포함) "
        "또한, 환율을 고려한 여행 경비 예산을 상세히 작성합니다. "
        "항목별 예산이 명확히 정리되어야 합니다."
    ),
    expected_output="한국어로 작성된 상세 예산표와 현지 맛집과 명소가 포함된 업데이트된 일자별 여행 일정",
    agent=local_recommendation_agent,
    context=[initial_travel_plan_task]  # 1단계 결과 참조
)

# 3단계: 전체 일정 최종 정리 (coordinator_agent)
final_coordinator_task = Task(
    description=(
        "앞선 모든 단계의 결과를 종합하여 최종적인 여행 일정을 깔끔하게 정리하고, "
        "고객에게 제시할 수 있도록 일자별 여행 일정과 예산을 명확하고 보기 쉽게 만듭니다."
    ),
    expected_output="한국어로 작성된 고객에게 전달할 최종 여행 일정 계획서(항공편 상세, 숙소 상세, 전체 비용, 일자별 일정표, 상세 예산표, 추가 정보)",
    agent=coordinator_agent,
    context=[local_recommendation_task]  # 2단계 결과 참조
)


