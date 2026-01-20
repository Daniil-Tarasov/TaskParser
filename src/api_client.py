import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CodeforcesProblem:
    contestId: int
    index: str
    name: str
    rating: Optional[int]
    solvedCount: int


class CodeforcesAPI:
    BASE_URL = "https://codeforces.com/api/"

    def get_problems(self, limit: int = 1000) -> Dict[str, Any]:
        """Получить список задач с рейтингами и solvedCount"""
        url = f"{self.BASE_URL}problemset.problems"
        params = {"limit": limit}

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_problem_tags(self, contest_id: int, index: str) -> List[str]:
        """Получить теги конкретной задачи"""
        url = f"{self.BASE_URL}problemset.problemTags"
        params = {"contestId": contest_id, "problemIndex": index}

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        return data["result"]["problemTags"][0]["tagList"] if data["status"] == "OK" else []
