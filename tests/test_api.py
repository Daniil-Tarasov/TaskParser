from src.api_client import CodeforcesAPI

def test_api_problems():
    api = CodeforcesAPI()
    data = api.get_problems(limit=10)
    assert data["status"] == "OK"
    assert len(data["result"]["problems"]) > 0
