
import sys
import json
from fastapi.testclient import TestClient
sys.path.append("/develop/python/projects/dfcx/myva/myva")

from myva.main import app  # noqa: E402

client = TestClient(app)


def read_case(path: str) -> dict:
    with open(path) as src:
        return json.load(src)


def test_find_nearest_location():
    payload = read_case("tests/cases/find_nearest_location.json")
    response = client.post("/find_nearest", json=payload)
    assert response.status_code == 200
    print(response.json())
