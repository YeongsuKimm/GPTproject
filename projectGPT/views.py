from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse, FileResponse
from io import BytesIO
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from openai import OpenAI
import json
from member.models import *



@method_decorator(csrf_exempt, name='dispatch')
class HistoryView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        try:
            stories = request.user.get_stories()
            stories_data = [
                {"topic": story.topic, "content": story.content, "created_at": story.created_at.strftime('%B %d, %Y, %I:%M %p'), "id": story.id}
                for story in stories
            ]
            return JsonResponse(stories_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')

import json
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        try:
            # Parse JSON body
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return JsonResponse({
                    "success": True,
                    "message": "login successful"
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": "Invalid username or password"
                }, status=401)

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "Invalid JSON format"
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }, status=500)


import json
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from member.models import CustomUser  # Make sure this import is correct

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(View):
    def get(self, request):
        return render(request, "signup.html")

    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Username already exists"
                }, status=409)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Email already exists"
                }, status=409)

            new_user = CustomUser.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({
                "success": True,
                "message": "Signup successful"
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "Invalid JSON"
            }, status=400)

        except IntegrityError:
            return JsonResponse({
                "success": False,
                "message": "Database error (possibly duplicate)"
            }, status=500)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }, status=500)




@method_decorator(csrf_exempt, name='dispatch')
class GenerateView(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "User not authenticated"}, status=401)
        # print(request.user.history)
        return render(request, "generate.html", context={"stories": request.user.get_stories()})
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "User not authenticated"}, status=401)
        data = json.loads(request.body)
        field = data.get("field")
        topic = data.get("topic")
        grade = data.get("grade")
        age = data.get("age")
        gender = data.get("gender")
        # client = OpenAI(api_key=open_ai_key)
        # response = client.chat.completions.create(
        #     model = "gpt-3.5-turbo",
        #     messages = [
        #         {"role":"system","content":f"Provide responses of the field {field} and topic {topic} to an audience that is {age} years old, in {grade} grade, and {gender}"},
        #         {"role": "user", "content": topic}
        #     ],
        #     temperature = 0
        # )

        # result = response.choices[0].message.content.strip()
        result = f"{field} + {topic} + {age} + {grade} + {gender}"
        context = {"content": result}
        request.user.add_story(content=context["content"], topic=topic)
        print(request.user.get_stories().count())
        return JsonResponse({
                "success": True,
                "data": context,
            }, status = 200)


class StoryGetView(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        try:
            story = Story.objects.get(id=id)
            story_data = [
                {"topic": story.topic, "content": story.content, "date": story.created_at.strftime('%B %d, %Y, %I:%M %p'), "id": story.id, "comments": story.get_comment_ids()}
            ]
            return JsonResponse(story_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, id):
        print(request.user.username)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        try:
            data = json.loads(request.body)
            content = data.get('content')
            story = Story.objects.get(id=id)
            comment = Comment.objects.create(
                user=request.user,
                story=story,
                content=content
            )
            return JsonResponse({'status': 'success', 'message': 'Comment added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


class StoryView(View):
    def get(self,request,id):
        return render(request, 'story.html')

class CommentModify(View):
    def get(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
            commentData = [
                {"content": comment.content, "created_at": comment.created_at, "user": comment.user.username}
            ]
            return JsonResponse(commentData, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            if request.user != comment.user:
                return JsonResponse({'error': 'Not authorized'}, status=403)
            comment.delete()
            return JsonResponse("comment successfuly deleted", status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    def put(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            if request.user != comment.user:
                return JsonResponse({'error': 'Not authorized'}, status=403)

            data = json.loads(request.body)
            new_content = data.get('content')
            if not new_content:
                return JsonResponse({'error': 'No content provided'}, status=400)

            comment.content = new_content
            comment.save()

            return JsonResponse({
                'message': 'Comment updated successfully',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at,
                }
            }, status=200)
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# class ImageGetView(View):
#     def get(self, request, id):













# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def download_story(request):
#     data = request.data
#     story_content = data.get('story')
#     if not story_content:
#         return Response({'error':'No story provided'}, status = 400)

#     #create a file-like object 
#     file_buffer = BytesIO()
#     file_buffer.write(story_content.encode('uft-8'))
#     file_buffer.seek(0)

#     response = FileResponse(file_buffer, as_attachment=True, filename='story.txt')

#     return response
