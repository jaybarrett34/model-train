"""
Quick test script to verify the API is working.
Run this after starting the backend server.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_create_project():
    """Test project creation."""
    print("Testing project creation...")
    project_data = {
        "name": "test-project",
        "objective": "Test project for API validation",
        "xml_patterns": [
            {
                "tag_name": "thinking",
                "description": "Internal reasoning",
                "constraints": "Must be valid XML"
            }
        ],
        "base_model": "unsloth/llama-2-7b-bnb-4bit"
    }

    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"Project created: {response.json()['name']}")
    else:
        print(f"Error: {response.json()}")
    print()


def test_list_projects():
    """Test listing projects."""
    print("Testing project listing...")
    response = requests.get(f"{BASE_URL}/projects")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total projects: {data['total']}")
    for project in data['projects']:
        print(f"  - {project['name']}: {project['objective']}")
    print()


def test_get_config():
    """Test config retrieval."""
    print("Testing config retrieval...")
    response = requests.get(f"{BASE_URL}/config")
    print(f"Status: {response.status_code}")
    config = response.json()
    print(f"Projects dir: {config['projects_dir']}")
    print(f"Models dir: {config['models_dir']}")
    print(f"Datasets dir: {config['datasets_dir']}")
    print()


def test_list_models():
    """Test model listing."""
    print("Testing model listing...")
    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total models: {data['total']}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("API Test Suite")
    print("=" * 50)
    print()

    try:
        test_health()
        test_create_project()
        test_list_projects()
        test_get_config()
        test_list_models()

        print("=" * 50)
        print("✅ All tests completed!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server")
        print("Make sure the backend is running: python -m backend.main")
    except Exception as e:
        print(f"❌ Error: {e}")
