import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from services.geocoding import geocode_location


@pytest.mark.asyncio
async def test_geocode_location_returns_coords_on_success():
    mock_result = MagicMock()
    mock_result.latitude = 42.6977
    mock_result.longitude = 23.3219

    with patch("services.geocoding.asyncio.to_thread", new=AsyncMock(return_value=mock_result)):
        result = await geocode_location("ул. Витоша 15, Лозенец", "Sofia")

    assert result == (42.6977, 23.3219)


@pytest.mark.asyncio
async def test_geocode_location_returns_none_when_not_found():
    with patch("services.geocoding.asyncio.to_thread", new=AsyncMock(return_value=None)):
        result = await geocode_location("nonexistent street", "Sofia")

    assert result is None


@pytest.mark.asyncio
async def test_geocode_location_returns_none_on_service_error():
    from geopy.exc import GeocoderServiceError
    with patch("services.geocoding.asyncio.to_thread", new=AsyncMock(side_effect=GeocoderServiceError("timeout"))):
        result = await geocode_location("ул. Раковски", "Sofia")

    assert result is None
