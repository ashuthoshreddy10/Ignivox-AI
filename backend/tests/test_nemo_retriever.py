import pytest
import json
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.nemo_retriever import NeMoRetriever, retriever
import numpy as np


@pytest.mark.anyio
async def test_nemo_retriever_initial_mode():
    test_retriever = NeMoRetriever()
    assert test_retriever.retriever_mode == "uninitialized"


@pytest.mark.anyio
async def test_nemo_retriever_mode_fallback():
    test_retriever = NeMoRetriever()
    
    with patch.object(test_retriever, "_knowledge_path") as mock_path:
        mock_path.return_value.exists.return_value = False
        
        # When no documents are loaded, mode should be local_fallback
        await test_retriever.load()
        assert test_retriever.retriever_mode == "local_fallback"


@pytest.mark.anyio
async def test_nemo_retriever_force_reinitialize():
    test_retriever = NeMoRetriever()
    
    with patch.object(test_retriever, "_knowledge_path") as mock_path:
        mock_path.return_value.exists.return_value = False
        await test_retriever.load()
        assert test_retriever.retriever_mode == "local_fallback"
        
        await test_retriever.force_reinitialize()
        assert test_retriever.retriever_mode == "local_fallback"


@pytest.mark.anyio
async def test_nemo_retriever_dimension_mismatch_warning_and_threshold_adjustment():
    test_retriever = NeMoRetriever()
    test_retriever.documents = [
        {"title": "Doc 1", "content": "RAG text", "category": "general"}
    ]
    # Set 384 dimensional document embeddings
    test_retriever.embeddings = np.zeros((1, 384))
    test_retriever._loaded = True
    test_retriever._mode = "nim_embeddings"
    
    # We will query with a 1024 dimensional embedding to trigger a mismatch
    mock_query_embeddings = [[0.0] * 1024]
    
    # We will capture logging output
    logger = logging.getLogger("app.services.nemo_retriever")
    
    with patch("app.services.nvidia_nim.nim_service.embed", AsyncMock(return_value=mock_query_embeddings)), \
         patch.object(test_retriever, "load", AsyncMock()) as mock_load, \
         patch.object(logger, "warning") as mock_warning, \
         patch.object(logger, "info") as mock_info:
        
        # We expect a mismatch because 384 (embeddings shape) != 1024 (query_emb shape)
        results = await test_retriever.retrieve("query text", top_k=5)
        
        # Verify logger.warning was called with JSON payload
        warning_calls = [call[0] for call in mock_warning.call_args_list]
        json_warn_call = None
        for call in warning_calls:
            if len(call) > 1 and "Dimension mismatch detected:" in call[0]:
                json_warn_call = call[1]
                break
        
        assert json_warn_call is not None
        structured_data = json.loads(json_warn_call)
        assert structured_data["expected_dim"] == 384
        assert structured_data["actual_dim"] == 1024
        assert structured_data["fallback_method"] == "character_hash"
        assert "timestamp" in structured_data
        
        # Verify mode fell back to local_fallback
        assert test_retriever.retriever_mode == "local_fallback"
        
        # Verify it logged threshold adjustment
        info_msgs = "".join([call[0][0] for call in mock_info.call_args_list])
        assert "Adjusted relevance threshold from 0.35 to 0.20" in info_msgs
