"""
Test Pulsus Storage Module

Tests the .pulsus/ directory creation and data persistence.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.pulsus.core.pulsus_storage import PulsusStorage


def test_storage_initialization():
    """Test that .pulsus/ directory structure is created."""
    print("\n" + "="*70)
    print("TEST: Storage Initialization")
    print("="*70)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = PulsusStorage(Path(temp_dir))

        # Check directory structure
        expected_dirs = [
            Path(temp_dir) / ".pulsus",
            Path(temp_dir) / ".pulsus" / "repositories",
            Path(temp_dir) / ".pulsus" / "cache" / "mcp_responses",
            Path(temp_dir) / ".pulsus" / "sessions",
        ]

        for expected_dir in expected_dirs:
            assert expected_dir.exists(), f"Directory not created: {expected_dir}"
            print(f"[OK] Created: {expected_dir.relative_to(temp_dir)}")

    print("\n[SUCCESS] Storage initialization test passed")
    return True


def test_save_and_retrieve_analysis():
    """Test saving and retrieving repository analysis."""
    print("\n" + "="*70)
    print("TEST: Save and Retrieve Analysis")
    print("="*70)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = PulsusStorage(Path(temp_dir))

        # Create mock analysis data
        test_repo_path = str(Path(temp_dir) / "test_repo")
        Path(test_repo_path).mkdir()

        analysis_data = {
            "llm_summary": "Test repository analysis summary",
            "health_status": "[EXCELLENT]",
            "statistics": {
                "total_files": 10,
                "total_functions": 50,
                "total_classes": 5
            },
            "issues_summary": {
                "total_issues": 3,
                "by_priority": {"HIGH": 1, "MEDIUM": 2}
            }
        }

        # Save analysis
        saved_paths = storage.save_repository_analysis(test_repo_path, analysis_data)
        print(f"[OK] Analysis saved to:")
        print(f"     Latest: {saved_paths.get('latest')}")
        print(f"     History: {saved_paths.get('history')}")

        # Verify files were created
        assert Path(saved_paths['latest']).exists(), "Latest file not created"
        assert Path(saved_paths['history']).exists(), "History file not created"

        # Retrieve latest analysis
        retrieved = storage.get_latest_analysis(test_repo_path)
        assert retrieved is not None, "Could not retrieve analysis"
        assert retrieved['analysis']['llm_summary'] == analysis_data['llm_summary']
        print(f"[OK] Retrieved analysis matches saved data")

        # Check repository info
        repo_hash = storage._get_repo_hash(test_repo_path)
        info_path = storage.pulsus_dir / "repositories" / repo_hash / "info.json"
        assert info_path.exists(), "Info file not created"

        with open(info_path, 'r') as f:
            info = json.load(f)
            print(f"[OK] Repository info:")
            print(f"     Name: {info['repository_name']}")
            print(f"     Hash: {info['repository_hash']}")
            print(f"     Analysis count: {info['analysis_count']}")

    print("\n[SUCCESS] Save and retrieve analysis test passed")
    return True


def test_analysis_history():
    """Test analysis history tracking."""
    import time

    print("\n" + "="*70)
    print("TEST: Analysis History Tracking")
    print("="*70)

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = PulsusStorage(Path(temp_dir))

        test_repo_path = str(Path(temp_dir) / "test_repo")
        Path(test_repo_path).mkdir()

        # Save multiple analyses
        for i in range(3):
            analysis_data = {
                "llm_summary": f"Analysis iteration {i+1}",
                "health_status": "[GOOD]",
                "statistics": {"iteration": i+1}
            }
            storage.save_repository_analysis(test_repo_path, analysis_data)
            print(f"[OK] Saved analysis {i+1}")
            # Small delay to ensure different timestamps
            time.sleep(0.1)

        # Retrieve history
        history = storage.get_analysis_history(test_repo_path, limit=10)
        assert len(history) == 3, f"Expected 3 analyses, got {len(history)}"
        print(f"[OK] Retrieved {len(history)} historical analyses")

        # Verify newest first
        assert history[0]['analysis']['statistics']['iteration'] == 3
        print(f"[OK] History ordered correctly (newest first)")

    print("\n[SUCCESS] Analysis history tracking test passed")
    return True


def test_list_repositories():
    """Test listing analyzed repositories."""
    print("\n" + "="*70)
    print("TEST: List Analyzed Repositories")
    print("="*70)

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = PulsusStorage(Path(temp_dir))

        # Create and analyze multiple test repositories
        repo_names = ["repo1", "repo2", "repo3"]
        for repo_name in repo_names:
            repo_path = str(Path(temp_dir) / repo_name)
            Path(repo_path).mkdir()

            analysis_data = {
                "llm_summary": f"Analysis of {repo_name}",
                "health_status": "[GOOD]"
            }
            storage.save_repository_analysis(repo_path, analysis_data)
            print(f"[OK] Analyzed {repo_name}")

        # List repositories
        repositories = storage.list_analyzed_repositories()
        assert len(repositories) == 3, f"Expected 3 repos, got {len(repositories)}"
        print(f"\n[OK] Found {len(repositories)} analyzed repositories:")

        for repo in repositories:
            print(f"     - {repo['repository_name']} (analyzed {repo['analysis_count']} time(s))")

    print("\n[SUCCESS] List repositories test passed")
    return True


def test_storage_stats():
    """Test storage statistics."""
    print("\n" + "="*70)
    print("TEST: Storage Statistics")
    print("="*70)

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = PulsusStorage(Path(temp_dir))

        # Create some test data
        test_repo_path = str(Path(temp_dir) / "test_repo")
        Path(test_repo_path).mkdir()

        analysis_data = {
            "llm_summary": "Test analysis",
            "health_status": "[GOOD]",
            "large_data": "x" * 10000  # Add some data
        }
        storage.save_repository_analysis(test_repo_path, analysis_data)

        # Get stats
        stats = storage.get_storage_stats()
        print(f"[OK] Storage statistics:")
        print(f"     Total repositories: {stats['total_repositories']}")
        print(f"     Total size: {stats['total_size_mb']} MB")
        print(f"     Directory: {stats['pulsus_directory']}")

        assert stats['total_repositories'] > 0
        assert stats['total_size_bytes'] > 0

    print("\n[SUCCESS] Storage statistics test passed")
    return True


def run_all_tests():
    """Run all storage tests."""
    print("\n" + "="*70)
    print("PULSUS STORAGE TESTS")
    print("="*70)
    print("Testing .pulsus/ directory creation and data persistence")
    print("="*70)

    tests = [
        ("Storage Initialization", test_storage_initialization),
        ("Save and Retrieve Analysis", test_save_and_retrieve_analysis),
        ("Analysis History", test_analysis_history),
        ("List Repositories", test_list_repositories),
        ("Storage Statistics", test_storage_stats),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n[FAILED] {test_name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for i, (test_name, _) in enumerate(tests, 1):
        status = "[PASS]" if i <= passed else "[FAIL]"
        print(f"  {status}   | {test_name}")

    print(f"\n  Total: {passed}/{len(tests)} tests passed ({passed*100//len(tests)}%)")
    print("="*70)

    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
