from crewai import Crew, Process
from agents import coordinator_agent, travel_info_agent, local_recommendation_agent
from tasks import initial_travel_plan_task, local_recommendation_task, final_coordinator_task

class TravelCoordinatorCrew():

    def crew(self) -> Crew:
        return Crew(
            agents=[travel_info_agent, local_recommendation_agent,coordinator_agent],
            tasks=[initial_travel_plan_task, local_recommendation_task, final_coordinator_task],
            process=Process.sequential,
            verbose=True
        )


