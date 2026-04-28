import os
import shutil
import pytest
import asyncio
from sqlalchemy import select
from app.database import engine, Base, async_session
from app.models import Feedback
from scripts.setup_project import run_setup

@pytest.mark.asyncio
async def test_setup_project_initializes_db_and_ingests():
    # Setup: Ensure clean state
    test_db = "test_feedback.db"
    test_chroma = "test_chroma_setup"
    test_data = "test_data_setup"
    
    if os.path.exists(test_db):
        os.remove(test_db)
    if os.path.exists(test_chroma):
        shutil.rmtree(test_chroma)
    if os.path.exists(test_data):
        shutil.rmtree(test_data)
        
    os.makedirs(test_data)
    with open(os.path.join(test_data, "test.txt"), "w") as f:
        f.write("This is a test document for setup script verification.")

    # Override environment variables for the test
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///./{test_db}"
    
    setup_success = False
    try:
        # Run setup
        await run_setup(data_dir=test_data, persist_db=test_chroma)
        
        # Verify DB initialization
        async with engine.begin() as conn:
            # Check if table exists by trying to select from it
            async with async_session() as session:
                result = await session.execute(select(Feedback))
                # Should not raise error
                assert True

        # Verify Vector Store creation
        assert os.path.exists(test_chroma)
        assert os.path.isdir(test_chroma)
        assert len(os.listdir(test_chroma)) > 0
        setup_success = True

    finally:
        # Cleanup
        if os.path.exists(test_db):
            # Close engine before removing file
            await engine.dispose()
            try:
                os.remove(test_db)
            except:
                pass
        
        # We might need to wait for ChromaDB to release file handles
        if os.path.exists(test_chroma):
            import gc
            import time
            gc.collect() # Try to force garbage collection of Chroma objects
            
            for i in range(5):
                try:
                    shutil.rmtree(test_chroma)
                    break
                except PermissionError:
                    time.sleep(1)
        
        if os.path.exists(test_data):
            shutil.rmtree(test_data)
        
        assert setup_success
