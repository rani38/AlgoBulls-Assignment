from django.http import JsonResponse
from rest_framework import status as st
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from django.shortcuts import get_object_or_404
from .models import Todo
import json


# Add To-Do
@api_view(['POST', 'GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def addtodo(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)

            title = data.get('title')
            description = data.get('description')
            due_date = data.get('due_date')
            status = data.get('status', 'OPEN')  # Default status
            tags = data.get('tags', [])

            # Validate required fields
            if not title or not description:
                return JsonResponse(
                    {"error": "Title and Description are required fields!"},
                    status=st.HTTP_400_BAD_REQUEST
                )

            # Create new To-Do item
            todo = Todo.objects.create(
                title=title,
                description=description,
                due_date=due_date if due_date else None,
                status=status,
                tags=tags,
            )

            return JsonResponse(
                {"message": "To-Do item added successfully!", "id": todo.id},
                status=st.HTTP_201_CREATED
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON format"},
                status=st.HTTP_400_BAD_REQUEST
            )

    # Handle GET request to list all todos
    todos = Todo.objects.all().values()
    return JsonResponse(list(todos), safe=False, status=st.HTTP_200_OK)


# Update To-Do
@api_view(['PATCH'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def updatetodo(request, id):
    try:
        # Get the existing To-Do object
        todo = get_object_or_404(Todo, id=id)

        # Parse JSON data
        data = json.loads(request.body)

        # Update fields only if provided
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        todo.due_date = data.get('due_date', todo.due_date)
        todo.status = data.get('status', todo.status)
        todo.tags = data.get('tags', todo.tags)
        todo.save()

        return JsonResponse(
            {"message": f"To-Do item with ID {id} updated successfully!"},
            status=st.HTTP_200_OK
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON format"},
            status=st.HTTP_400_BAD_REQUEST
        )


# Delete To-Do
@api_view(['DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def deletetodo(request, id):
    todo = get_object_or_404(Todo, id=id)
    todo.delete()
    return JsonResponse(
        {"message": f"To-Do item with ID {id} deleted successfully!"},
        status=st.HTTP_200_OK
    )


# Show All To-Dos
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def showtodos(request):
    todos = Todo.objects.all().values()
    return JsonResponse(
        list(todos),
        safe=False,
        status=st.HTTP_200_OK
    )


# Show To-Do by ID
@api_view(['GET'])
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
