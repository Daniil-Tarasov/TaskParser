import pytest
import requests

from src.api_client import CodeforcesAPI, CodeforcesProblem


class TestCodeforcesAPI:
    """Тесты CodeforcesAPI"""

    @pytest.fixture
    def api(self):
        return CodeforcesAPI()

    def test_api_problems(self, api):
        data = api.get_problems(limit=10)
        assert data["status"] == "OK"
        assert len(data["result"]["problems"]) > 0

    @pytest.mark.parametrize(
        "tags, expected_params",
        [
            (None, {"limit": 1000}),
            ("math", {"limit": 1000, "tags": "math"}),
            ("dp,greedy", {"limit": 1000, "tags": "dp,greedy"}),
        ],
    )
    def test_get_problems_params(self, requests_mock, api, tags, expected_params):
        """Проверяем параметры запроса"""

        requests_mock.get(
            "https://codeforces.com/api/problemset.problems",
            json={"status": "OK", "result": {"problems": [], "problemStatistics": []}},
        )

        result = api.get_problems(tags=tags, limit=1000)
        assert result["status"] == "OK"

    def test_get_problems_success(self, requests_mock, api):
        """Успешный запрос проблем"""

        mock_data = {
            "status": "OK",
            "result": {
                "problems": [{"contestId": 2185, "index": "A", "name": "Perfect Root", "rating": 1200}],
                "problemStatistics": [{"contestId": 2185, "index": "A", "solvedCount": 30850}],
            },
        }

        requests_mock.get("https://codeforces.com/api/problemset.problems", json=mock_data)

        result = api.get_problems(limit=1)
        assert result["status"] == "OK"
        assert len(result["result"]["problems"]) == 1
        assert result["result"]["problems"][0]["contestId"] == 2185

    def test_get_problems_network_error(self, requests_mock, api):
        """Сетевые ошибки"""

        requests_mock.get("https://codeforces.com/api/problemset.problems", status_code=500)

        result = api.get_problems()
        assert result["status"] == "FAILED"

    def test_get_problems_timeout(self, requests_mock, api):
        """Timeout"""

        requests_mock.get("https://codeforces.com/api/problemset.problems", exc=requests.exceptions.Timeout)

        result = api.get_problems()
        assert result["status"] == "FAILED"

    def test_get_problem_tags_success(self, requests_mock, api):
        """Теги задачи"""

        mock_tags = {
            "status": "OK",
            "result": {"problemTags": [{"contestId": 2185, "index": "A", "tagList": ["math", "constructive"]}]},
        }

        requests_mock.get("https://codeforces.com/api/problemset.problemTags", json=mock_tags)

        tags = api.get_problem_tags(2185, "A")
        assert tags == ["math", "constructive"]

    def test_get_problem_tags_not_found(self, requests_mock, api):
        """Задача не найдена"""

        requests_mock.get(
            "https://codeforces.com/api/problemset.problemTags", json={"status": "OK", "result": {"problemTags": []}}
        )

        tags = api.get_problem_tags(9999, "Z")
        assert tags == []

    def test_get_problem_tags_error(self, requests_mock, api):
        """API ошибка"""

        requests_mock.get("https://codeforces.com/api/problemset.problemTags", status_code=404)

        tags = api.get_problem_tags(2185, "A")
        assert tags == []


class TestCodeforcesProblemDataclass:
    """Тесты dataclass"""

    def test_codeforces_problem_creation(self):
        """Создание класса CodeforcesProblem"""
        problem = CodeforcesProblem(
            contestId=2185, index="A", name="Perfect Root", rating=1200, solvedCount=30850, tags=["math"]
        )

        assert problem.contestId == 2185
        assert problem.index == "A"
        assert problem.name == "Perfect Root"
        assert problem.rating == 1200
        assert problem.solvedCount == 30850
        assert problem.tags == ["math"]

    def test_optional_fields(self):
        problem = CodeforcesProblem(contestId=None, index="B", name="No Rating", rating=None, solvedCount=0)

        assert problem.contestId is None
        assert problem.rating is None
