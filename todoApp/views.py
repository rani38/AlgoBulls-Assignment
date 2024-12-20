from django.http import JsonResponse
from rest_framework import status as st
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (
    permission_classes,
    authentication_classes,
    api_view,
)
from django.shortcuts import get_object_or_404
from .models import Todo, Tag
import json
import datetime


# Add To-Do
@api_view(["POST", "GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def addtodo(request):
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description")
            due_date = data.get("due_date")
            status = data.get("status", "OPEN")  # Default status
            tags = data.get("tags", [])

            # check due_date is not in past
            if due_date:
                if due_date < str(datetime.date.today()):
                    return JsonResponse(
                        {"error": "Due date cannot be in the past!"},
                        status=st.HTTP_400_BAD_REQUEST,
                    )

            # Validate required fields
            if not title or not description:
                return JsonResponse(
                    {"error": "Title and Description are required fields!"},
                    status=st.HTTP_400_BAD_REQUEST,
                )

            if len(title) > 100 or len(description) > 1000:
                return JsonResponse(
                    {
                        "error": "Title should be less than 100 characters and Description should be less than 1000 characters!"
                    },
                    status=st.HTTP_400_BAD_REQUEST,
                )

            # validate if status is in list of choices or not
            status_choices = [
                "OPEN",
                "WORKING",
                "COMPLETED",
                "PENDING REVIEW",
                "OVERDUE",
                "CANCELLED",
            ]
            if status not in status_choices or status == "":
                return JsonResponse(
                    {
                        "error": "Status should be one of the following: 'OPEN', 'WORKING', 'COMPLETED', 'PENDING REVIEW', 'OVERDUE', 'CANCELLED'"
                    },
                    status=st.HTTP_400_BAD_REQUEST,
                )

            # done with checks push in database
            # Create new To-Do item
            # tags are many to many realtion so we need to pass list of tags
            # Process tags
            tag_objects = []
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    # Create tag if it doesn't exist
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    tag_objects.append(tag)

            # Create the To-Do item
            todo = Todo.objects.create(
                title=title,
                description=description,
                due_date=due_date,
                status=status,
            )
            todo.tags.set(tag_objects)

            return JsonResponse(
                {"message": "To-Do item added successfully!", "id": todo.id},
                status=st.HTTP_201_CREATED,
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON format"}, status=st.HTTP_400_BAD_REQUEST
            )

    # Handle GET request to list all todos
    todos = Todo.objects.all().values()
    return JsonResponse(list(todos), safe=False, status=st.HTTP_200_OK)


# Update To-Do
@api_view(["PATCH"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def updatetodo(request, id):
    try:
        # Get the existing To-Do object
        todo = get_object_or_404(Todo, id=id)

        # Parse JSON data
        data = json.loads(request.body)

        # Update fields only if provided

        # check for length of title and description
        if len(data.get("description")) > 1000 or len(data.get("title")) > 100:
            return JsonResponse(
                {
                    "error": "Title should be less than 100 characters and Description should be less than 1000 characters!"
                },
                status=st.HTTP_400_BAD_REQUEST,
            )
        todo.title = data.get("title", todo.title)
        todo.description = data.get("description", todo.description)

        # check for due date
        if data.get("due_date") and data.get("due_date") < str(datetime.date.today()):
            return JsonResponse(
                {"error": "Due date cannot be in the past!"},
                status=st.HTTP_400_BAD_REQUEST,
            )
        todo.due_date = data.get("due_date", todo.due_date)

        # check for status
        if (data.get("status") == "") or data.get("status") not in [
            "OPEN",
            "WORKING",
            "COMPLETED",
            "PENDING REVIEW",
            "OVERDUE",
            "CANCELLED",
        ]:
            return JsonResponse(
                {
                    "error": "Status should be one of the following: 'OPEN', 'WORKING', 'COMPLETED', 'PENDING REVIEW', 'OVERDUE', 'CANCELLED'"
                },
                status=st.HTTP_400_BAD_REQUEST,
            )
        todo.status = data.get("status", todo.status)

        # check for tags
        tag_objects = []
        for tag_name in data.get('tags'):
            tag_name = tag_name.strip()
            if tag_name:
                # Create tag if it doesn't exist
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tag_objects.append(tag)
        todo.tags.set(tag_objects)
        todo.save()

        return JsonResponse(
            {"message": f"To-Do item with ID {id} updated successfully!"},
            status=st.HTTP_200_OK,
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON format"}, status=st.HTTP_400_BAD_REQUEST
        )


# Delete To-Do
@api_view(["DELETE"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def deletetodo(request, id):
    todo = get_object_or_404(Todo, id=id)
    todo.delete()
    return JsonResponse(
        {"message": f"To-Do item with ID {id} deleted successfully!"},
        status=st.HTTP_200_OK,
    )


# Show All To-Dos
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def showtodos(request):
    todos = Todo.objects.all().values()
    return JsonResponse(list(todos), safe=False, status=st.HTTP_200_OK)


# Show To-Do by ID
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def showtodo(request, id):
    todo = get_object_or_404(Todo, id=id)
    # Exclude private attributes
    todo_data = {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "due_date": todo.due_date,
        "status": todo.status,
        "tags": todo.tags,
    }
    return JsonResponse(todo_data, status=st.HTTP_200_OK)
