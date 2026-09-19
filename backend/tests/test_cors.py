"""
CORS Configuration and Middleware Tests.

Verifies that FastAPI properly handles CORS requests for:
1. Production origins: https://genecureai.vercel.app, https://genecureaii.vercel.app
2. Vercel deployment/preview origins: https://genecureaii-2v5ztn5z9-sarita-damodar-naik.vercel.app
3. Dynamic project preview origins matching ALLOWED_ORIGIN_REGEX
4. Safely rejects unauthorized/malicious origins
"""
import pytest
import re
from app.core.config import settings


def test_cors_settings_configuration():
    """Verify settings contains expected origins and valid regex pattern."""
    assert "https://genecureai.vercel.app" in settings.ALLOWED_ORIGINS
    assert "https://genecureaii.vercel.app" in settings.ALLOWED_ORIGINS
    assert "https://genecureaii-2v5ztn5z9-sarita-damodar-naik.vercel.app" in settings.ALLOWED_ORIGINS

    assert settings.ALLOWED_ORIGIN_REGEX is not None
    compiled_regex = re.compile(settings.ALLOWED_ORIGIN_REGEX)

    # Allowed targets
    assert compiled_regex.fullmatch("https://genecureai.vercel.app")
    assert compiled_regex.fullmatch("https://genecureaii.vercel.app")
    assert compiled_regex.fullmatch("https://genecureaii-2v5ztn5z9-sarita-damodar-naik.vercel.app")
    assert compiled_regex.fullmatch("https://genecureai-git-main-sarita-damodar-naik.vercel.app")
    assert compiled_regex.fullmatch("https://genecureai-preview-abc.vercel.app")
    assert compiled_regex.fullmatch("https://genecureaii-test-branch.vercel.app")

    # Disallowed targets
    assert not compiled_regex.fullmatch("https://otherproject.vercel.app")
    assert not compiled_regex.fullmatch("https://evil-genecureai.vercel.app")
    assert not compiled_regex.fullmatch("https://genecureai.vercel.app.attacker.com")
    assert not compiled_regex.fullmatch("http://genecureai.vercel.app")


@pytest.mark.parametrize(
    "origin",
    [
        "https://genecureai.vercel.app",
        "https://genecureaii.vercel.app",
        "https://genecureaii-2v5ztn5z9-sarita-damodar-naik.vercel.app",
        "https://genecureai-preview-123.vercel.app",
        "https://genecureaii-pr-45-sarita-damodar-naik.vercel.app",
    ],
)
@pytest.mark.asyncio
async def test_cors_allowed_origins_simple_request(async_client, origin: str):
    """Verify simple GET request from allowed Vercel origins receives CORS headers."""
    response = await async_client.get(
        "/api/health",
        headers={"Origin": origin},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.parametrize(
    "origin",
    [
        "https://genecureai.vercel.app",
        "https://genecureaii.vercel.app",
        "https://genecureaii-2v5ztn5z9-sarita-damodar-naik.vercel.app",
        "https://genecureai-preview-123.vercel.app",
        "https://genecureaii-pr-45-sarita-damodar-naik.vercel.app",
    ],
)
@pytest.mark.asyncio
async def test_cors_allowed_origins_preflight_request(async_client, origin: str):
    """Verify preflight OPTIONS request from allowed Vercel origins succeeds."""
    response = await async_client.options(
        "/api/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "GET" in response.headers.get("access-control-allow-methods", "")


@pytest.mark.parametrize(
    "origin",
    [
        "https://evil-site.com",
        "https://attacker.vercel.app",
        "https://evil-genecureai.vercel.app",
        "https://genecureai.vercel.app.attacker.com",
        "http://genecureai.vercel.app",
    ],
)
@pytest.mark.asyncio
async def test_cors_disallowed_origins_rejected(async_client, origin: str):
    """Verify requests from unauthorized origins do not receive CORS allow headers."""
    # Simple request
    response = await async_client.get(
        "/api/health",
        headers={"Origin": origin},
    )
    assert response.headers.get("access-control-allow-origin") is None

    # Preflight request
    options_resp = await async_client.options(
        "/api/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert options_resp.headers.get("access-control-allow-origin") is None
