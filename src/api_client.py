import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeforcesProblem:
    contestId: Optional[int]
    index: str
    name: str
    rating: Optional[int]
    solvedCount: int
    tags: List[str] = None


class CodeforcesAPI:
    BASE_URL = "https://codeforces.com/api/"

    def get_problems(self, tags: str = None, limit: int = 1000) -> Dict[str, Any]:
        """Получить задачи с фильтром по тегам"""
        url = f"{self.BASE_URL}problemset.problems"
        params = {"limit": limit}
        if tags:
            params["tags"] = tags

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API error: {e}")
            return {"status": "FAILED"}

    def get_problem_tags(self, contest_id: int, index: str) -> List[str]:
        """Теги конкретной задачи"""
        url = f"{self.BASE_URL}problemset.problemTags"
        params = {"contestId": contest_id, "problemIndex": index}

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["result"]["problemTags"][0]["tagList"] if data["status"] == "OK" else []
        except:
            return []
