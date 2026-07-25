from backend.agents.director_agent import DirectorAgent

class DirectorService:
    """
    DirectorService links the director controller to the DirectorAgent orchestrator.
    """

    def __init__(self):
        self.director_agent = DirectorAgent()

    def process_video_job(self, job_id: str) -> dict:
        """
        Triggers the multi-agent pipeline orchestrator for the given job_id.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            dict: Combined results dictionary containing analysis and highlights.
        """
        # Delegate to the DirectorAgent
        return self.director_agent.run_pipeline(job_id)
