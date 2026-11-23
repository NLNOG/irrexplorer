import pytest

from irrexplorer.api.messages import MessageType

pytestmark = pytest.mark.asyncio


async def test_messages(client):
    response = await client.get("/api/messages/")
    assert response.status_code == 200
    messages = {message["key"]: message for message in response.json()}
    assert messages["expected_irr_no_route_object"] == {
        "key": "expected_irr_no_route_object",
        "category": "warning",
        "text": "Expected route object in <IRR>, but only found in other IRRs",
        "explanation": MessageType.EXPECTED_IRR_NO_ROUTE_OBJECT.explanation,
    }
    assert messages["special_use_overlap"]["text"] == (
        "Overlaps with <NAME> special use prefix <PREFIX>"
    )
