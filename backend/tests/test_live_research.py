import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.services.live_research import (
    LiveResearchService,
    LiveResearchResult,
    DuckDuckGoBlockedError,
    detect_ddg_block
)
import httpx


def test_detect_ddg_block_202():
    response = httpx.Response(202, text="Challenge")
    with pytest.raises(DuckDuckGoBlockedError) as exc_info:
        detect_ddg_block(response)
    assert "status code 202" in str(exc_info.value)


def test_detect_ddg_block_captcha():
    response = httpx.Response(200, text="Please solve this ddg-captcha to continue.")
    with pytest.raises(DuckDuckGoBlockedError) as exc_info:
        detect_ddg_block(response)
    assert "CAPTCHA" in str(exc_info.value)


def test_detect_ddg_block_zero_results():
    response = httpx.Response(200, text="<html><body>No results found</body></html>")
    with pytest.raises(DuckDuckGoBlockedError) as exc_info:
        detect_ddg_block(response)
    assert "No search results" in str(exc_info.value)


@pytest.mark.anyio
async def test_live_research_success():
    service = LiveResearchService()
    mock_html = """
    <html>
        <body>
            <a class="result__snippet" href="https://html.duckduckgo.com/html/redirect?uddg=https%3A%2F%2Fexample.com">Snippet 1</a>
            <a class="result__title">Title 1</a>
        </body>
    </html>
    """
    
    with patch.object(service.client, "get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        
        results = await service.search("success query")
        
        assert not results.fallback
        assert results.reason is None
        assert len(results) == 1
        assert results[0]["title"] == "Title 1"
        assert results[0]["url"] == "https://example.com"
        assert results[0]["snippet"] == "Snippet 1"


@pytest.mark.anyio
async def test_live_research_fallback_chain_success_on_retry():
    service = LiveResearchService()
    mock_html = """
    <html>
        <body>
            <a class="result__snippet" href="https://example.com">Snippet 2</a>
            <a class="result__title">Title 2</a>
        </body>
    </html>
    """
    
    with patch.object(service.client, "get") as mock_get, patch("asyncio.sleep", return_value=None) as mock_sleep:
        # First call fails with block
        mock_response_fail = AsyncMock()
        mock_response_fail.status_code = 202
        mock_response_fail.text = "Blocked"
        mock_response_fail.raise_for_status = lambda: None
        
        # Second call succeeds
        mock_response_success = AsyncMock()
        mock_response_success.status_code = 200
        mock_response_success.text = mock_html
        mock_response_success.raise_for_status = lambda: None
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        results = await service.search("retry query")
        
        assert not results.fallback
        assert results.reason is None
        assert len(results) == 1
        assert results[0]["title"] == "Title 2"
        assert mock_sleep.called
        mock_sleep.assert_called_once_with(2.0)
        
        # Verify different User-Agents
        assert mock_get.call_count == 2
        ua1 = mock_get.call_args_list[0][1]["headers"]["User-Agent"]
        ua2 = mock_get.call_args_list[1][1]["headers"]["User-Agent"]
        assert ua1 != ua2


@pytest.mark.anyio
async def test_live_research_complete_fallback_failure():
    service = LiveResearchService()
    
    with patch.object(service.client, "get") as mock_get, patch("asyncio.sleep", return_value=None) as mock_sleep:
        # Both calls fail
        mock_response_fail1 = AsyncMock()
        mock_response_fail1.status_code = 202
        mock_response_fail1.text = "Blocked"
        mock_response_fail1.raise_for_status = lambda: None
        
        mock_response_fail2 = AsyncMock()
        mock_response_fail2.status_code = 200
        mock_response_fail2.text = "CAPTCHA required"
        mock_response_fail2.raise_for_status = lambda: None
        
        mock_get.side_effect = [mock_response_fail1, mock_response_fail2]
        
        results = await service.search("failing query")
        
        assert results.fallback
        assert "CAPTCHA" in results.reason
        assert len(results) == 1
        assert results[0]["url"] == "https://www.ipcc.ch/reports"
        assert "Static Domain Metrics for failing query" in results[0]["title"]
        assert results[0]["is_fallback"] is True
        assert "enterprise application optimization" in results[0]["snippet"]
        mock_sleep.assert_called_once_with(2.0)


@pytest.mark.anyio
async def test_live_research_domain_specific_fallback():
    service = LiveResearchService()
    service.current_domain = "fintech"
    
    with patch.object(service.client, "get") as mock_get, patch("asyncio.sleep", return_value=None):
        # Both calls fail
        mock_response_fail = AsyncMock()
        mock_response_fail.status_code = 202
        mock_response_fail.text = "Blocked"
        mock_response_fail.raise_for_status = lambda: None
        mock_get.side_effect = [mock_response_fail, mock_response_fail]
        
        results = await service.search("micro-lending platform")
        assert results.fallback
        assert len(results) == 1
        assert results[0]["is_fallback"] is True
        assert "secure financial platform managing transaction ledgers" in results[0]["snippet"]


@pytest.mark.anyio
async def test_live_research_jitter_sleep_execution():
    service = LiveResearchService()
    service._force_jitter_sleep_for_testing = True
    
    mock_html = """
    <html>
        <body>
            <a class="result__snippet" href="https://example.com">Snippet</a>
            <a class="result__title">Title</a>
        </body>
    </html>
    """
    
    with patch.object(service.client, "get") as mock_get, patch("asyncio.sleep", return_value=None) as mock_sleep:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        
        await service.search("jitter test")
        
        assert mock_sleep.call_count >= 1
        first_sleep_arg = mock_sleep.call_args_list[0][0][0]
        assert 1.5 <= first_sleep_arg <= 3.5
