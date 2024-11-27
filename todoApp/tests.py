from django.test import TestCase
from django.urls import reverse
from rest_framework import status as st
from .models import Todo
from django.contrib.auth.models import User
from rest_framework.test import APIClient
import json
from django.utils.crypto import get_random_string


class TodoViewsTestCase(TestCase):

    def setUp(self):
        print("Setting up test data...")
        # Create a test user for Basic Authentication
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Add test To-Do items
        self.todo1 = Todo.objects.create(
            title="Test Todo 1",
            description="Description for Test Todo 1",
            due_date="2024-11-30",
            status="OPEN",
            tags=["test", "todo1"],
        )
        self.todo2 = Todo.objects.create(
            title="Test Todo 2",
            description="Description for Test Todo 2",
            due_date="2024-12-01",
            status="WORKING",
            tags=["test", "todo2"],
        )

        # Use APIClient for testing
        self.client = APIClient()

    def authenticate(self):
        print("Authenticating client...")
        # Log in and set Basic Authentication credentials
        self.client.login(username="testuser", password="testpassword")
        # Base64 encoding of "testuser:testpassword"
        self.client.credentials(HTTP_AUTHORIZATION="Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk")

    def test_add_todo(self):
        print("Testing add todo...")
        self.authenticate()
        url = reverse("addtodo")
        data = {
            "title": "New Todo",
            "description": "Description for New Todo",
            "due_date": "2024-11-30",
            "status": "OPEN",
            "tags": ["new", "todo"],
        }
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, st.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 3)

    def test_list_todos(self):
        print("Testing list todos...")
        self.authenticate()
        url = reverse("addtodo")
        response = self.client.get(url)
        self.assertEqual(response.status_code, st.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_update_todo(self):
        print("Testing update todo...")
        self.authenticate()
        url = reverse("updatetodo", args=[self.todo1.id])
        data = {"title": "Updated Todo 1", "status": "COMPLETED"}
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, st.HTTP_200_OK)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, "Updated Todo 1")
        self.assertEqual(self.todo1.status, "COMPLETED")

    def test_delete_todo(self):
        print("Testing delete todo...")
        self.authenticate()
        url = reverse("deletetodo", args=[self.todo1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, st.HTTP_200_OK)
        self.assertEqual(Todo.objects.count(), 1)

    def test_show_todos(self):
        print("Testing show todos...")
        self.authenticate()
        url = reverse("showtodos")
        response = self.client.get(url)
        self.assertEqual(response.status_code, st.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_show_todo_by_id(self):
        print("Testing show todo by ID...")
        self.authenticate()
        url = reverse("showtodo", args=[self.todo1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, st.HTTP_200_OK)
        self.assertEqual(response.json()["title"], self.todo1.title)

    def test_authentication_required(self):
        print("Testing authentication required...")
        url = reverse("addtodo")
        response = self.client.get(url)
        self.assertEqual(response.status_code, st.HTTP_401_UNAUTHORIZED)


print("Running tests...")


class TodoIntegrationTestCase(TestCase):

    def setUp(self):
        print("Setting up test data...")
        # Create a test user for Basic Authentication
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Use APIClient for testing
        self.client = APIClient()

        # Authenticate the client
        self.client.login(username="testuser", password="testpassword")
        # Base64 encoding of "testuser:testpassword"
        self.client.credentials(HTTP_AUTHORIZATION="Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk")

    def test_create_retrieve_update_delete_todo(self):
        # Test the full CRUD functionality
        print("Testing full CRUD functionality...")
        # 1. Create a new To-Do
        create_url = reverse("addtodo")
        create_data = {
            "title": "Integration Test Todo",
            "description": "Integration test description",
            "due_date": "2024-11-30",
            "status": "OPEN",
            "tags": ["integration", "test"],
        }
        create_response = self.client.post(
            create_url, data=json.dumps(create_data), content_type="application/json"
        )
        self.assertEqual(
            create_response.status_code, st.HTTP_201_CREATED, "Test failed"
        )
        todo_id = create_response.json().get("id")

        # 2. Retrieve the created To-Do
        retrieve_url = reverse("showtodo", args=[todo_id])
        retrieve_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_response.status_code, st.HTTP_200_OK)
        self.assertEqual(retrieve_response.json()["title"], "Integration Test Todo")

        # 3. Update the To-Do
        update_url = reverse("updatetodo", args=[todo_id])
        update_data = {"title": "Updated Integration Test Todo", "status": "COMPLETED"}
        update_response = self.client.patch(
            update_url, data=json.dumps(update_data), content_type="application/json"
        )
        self.assertEqual(update_response.status_code, st.HTTP_200_OK)

        # Verify the update
        retrieve_updated_response = self.client.get(retrieve_url)
        self.assertEqual(
            retrieve_updated_response.json()["title"], "Updated Integration Test Todo"
        )
        self.assertEqual(retrieve_updated_response.json()["status"], "COMPLETED")

        # 4. Delete the To-Do
        delete_url = reverse("deletetodo", args=[todo_id])
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, st.HTTP_200_OK)

        # Verify the deletion
        retrieve_deleted_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_deleted_response.status_code, st.HTTP_404_NOT_FOUND)

    def test_authentication_required(self):
        print("Testing authentication required...")
        # Test accessing a view without authentication
        self.client.credentials()  # Remove authentication headers
        url = reverse("addtodo")
        response = self.client.get(url)
        self.assertEqual(response.status_code, st.HTTP_401_UNAUTHORIZED)

    def test_invalid_field_values(self):
        # Test creating a To-Do with missing required fields
        create_url = reverse("addtodo")
        invalid_data = {
            "description": "Description without a title",
            "status": "OPEN",
        }
        response = self.client.post(
            create_url, data=json.dumps(invalid_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, st.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())
        # No new To-Do should be created
        self.assertEqual(Todo.objects.count(), 2)

        # Test creating a To-Do with an invalid date
        invalid_data["title"] = "Invalid Date Test"
        invalid_data["due_date"] = "invalid-date"
        response = self.client.post(
            create_url, data=json.dumps(invalid_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, st.HTTP_400_BAD_REQUEST)

    def test_nonexistent_resource_ids(self):
        print("Testing nonexistent resource IDs...")
        # Test updating a nonexistent To-Do
        # Assuming 9999 is a nonexistent ID
        update_url = reverse("updatetodo", args=[9999])
        update_data = {
            "title": "Nonexistent Update",
        }
        response = self.client.patch(
            update_url, data=json.dumps(update_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, st.HTTP_404_NOT_FOUND)

        # Test deleting a nonexistent To-Do
        # Assuming 9999 is a nonexistent ID
        delete_url = reverse("deletetodo", args=[9999])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, st.HTTP_404_NOT_FOUND)

        # Test retrieving a nonexistent To-Do
        retrieve_url = reverse("showtodo", args=[9999])
        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, st.HTTP_404_NOT_FOUND)

    def test_large_payload(self):
        print("Testing large payload...")
        # Generate a large string for the title and description
        large_string = get_random_string(length=10000)
        create_url = reverse("addtodo")
        large_data = {
            "title": large_string,
            "description": large_string,
            "due_date": "2024-12-31",
            "status": "OPEN",
            "tags": ["stress", "test"],
        }
        response = self.client.post(
            create_url, data=json.dumps(large_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, st.HTTP_201_CREATED)

        # Verify the created To-Do exists in the database
        todo_id = response.json().get("id")
        retrieve_url = reverse("showtodo", args=[todo_id])
        retrieve_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_response.status_code, st.HTTP_200_OK)
        self.assertEqual(retrieve_response.json()["title"], large_string)

    def test_stress_testing_multiple_todos(self):
        # Simulate creating 100 To-Do items
        create_url = reverse("addtodo")
        for i in range(100):
            data = {
                "title": f"Stress Test Todo {i}",
                "description": f"Description for Stress Test Todo {i}",
                "due_date": "2024-12-31",
                "status": "OPEN",
                "tags": [f"test{i}"],
            }
            response = self.client.post(
                create_url, data=json.dumps(data), content_type="application/json"
            )
            self.assertEqual(response.status_code, st.HTTP_201_CREATED)

        # Verify 1000 additional To-Do items were created
        todos = Todo.objects.all()
        self.assertEqual(todos.count(), 1002)  # 2 pre-existing + 100 new
