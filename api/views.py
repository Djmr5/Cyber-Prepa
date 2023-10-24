# Views (Logic) for API calls.
from django.http import JsonResponse
from datetime import timedelta
from rental.models import Game, Plays, Student, Log, Sanction
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from json import loads
import json

# Index calls
def get_start_times(request):
    if request.method == 'GET':
        try:
            games = Game.objects.filter(show=True).values('start_time')
            data = []
            for game in games:
                original_time = game['start_time']
                # For new created games start_time is None, handle it by adding a default time
                # for displaying the game in the frontend; cards.js line 30
                if original_time is None:
                    data.append({'time': 'Jan 1, 2000 00:00:00'})
                    continue
                subtracted_time = original_time - timedelta(hours=5, minutes=5)
                formatted_time = subtracted_time.strftime('%b %d, %Y %H:%M:%S')
                data.append({'time': formatted_time})
            return JsonResponse(data, safe=False)
        except:
            return JsonResponse({'status': 'error'})
    
def get_available_games(request):
    if request.method == 'GET':
        try:
            games = Game.objects.filter(show=True).values('available')
            data = []
            for game in games:
                data.append({'available': game['available']})
            return JsonResponse(data, safe=False)
        except:
            return JsonResponse({'status': 'error'})
    
def set_play_ended(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            play = Plays.objects.filter(student__id=student_id).latest('time')
            play.ended = True
            play.save()
            log = Log.objects.create(actionPerformed=f' Termina sesión de juego de: {student_id}', user=request.user)
            log.save()
            return JsonResponse({'status': 'success'})
        except Plays.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Play not found'})


def condiciones_para_juego(student_id):
    """Verifica si el estudiante tiene sanciones presentes"""
    current_datetime = timezone.now()

    active_sanctions = Sanction.objects.filter(
        student__id=student_id,
        end_time__gt=current_datetime
    ).exists()

    return not active_sanctions


def add_student_to_game(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        game_id = request.POST.get('game_id')
        try:
            game = Game.objects.get(id=game_id)
            student, created = Student.objects.get_or_create(id=student_id)

            if created:
                student.save()

            if condiciones_para_juego(student_id):
                is_playing = Plays.objects.filter(student__id=student_id, ended=False).exists()
                if is_playing:
                    return JsonResponse({'status': 'error', 'message': 'Student is already playing'})
                play = Plays.objects.create(game=game, student=student)
                play.save()
                log = Log.objects.create(actionPerformed=f' Inicia sesión de juego para: {student_id}', user=request.user)
                log.save()
                return JsonResponse({'status': 'success', 'message': 'Student added to the game'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Student has active sanctions'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


def add_student_to_sanctioned(request):
    if request.method == 'POST':
        data = loads(request.body)
        student_id = data['student_id']
        cause = data['cause']
        days = data['days']

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            student = Student.objects.create(id=student_id)

        current_time = timezone.now()
        end_time = current_time + timezone.timedelta(days=int(days))
        sanction = Sanction(
            student=student,
            cause=cause,
            start_time=current_time,
            end_time=end_time,
        )
        sanction.save()
        return JsonResponse({'status': 'success'})


# Admin CRUD datatables calls
def get_plays_list(request):
    if request.method == 'GET':
        plays = (
            Plays.objects
            .select_related('game')
            .values('id', 'student_id', 'game__name', 'ended', 'time')
        )
        data = {'plays': list(plays)}
        return JsonResponse(data, safe=False)
    
def get_students_list(request):
    if request.method == 'GET':
        students = (
            Student.objects
            .values('id', 'name')
        )
        data = {'students': list(students)}
        return JsonResponse(data, safe=False)
    
def get_games_list(request):
    if request.method == 'GET':
        games = (
            Game.objects
            .values('id', 'name', 'displayName', 'available', 'show')
        )
        data = {'games': list(games)}
        return JsonResponse(data, safe=False)
    
def get_logs_list(request):
    if request.method == 'GET':
        logs = (
            Log.objects
            .select_related('user')
            .values('id', 'actionPerformed', 'user__username', 'time')
        )
        data = {'logs': list(logs)}
        return JsonResponse(data, safe=False)
    
def get_sanctions_list(request):
    if request.method == 'GET':
        sanctions = (
            Sanction.objects
            .select_related('student')
            .values('id', 'cause', 'student__id', 'play_id', 'start_time', 'end_time')
        )
        data = {'sanctions': list(sanctions)}
        return JsonResponse(data, safe=False)
    
def get_users_list(request):
    if request.method == 'GET':
        users = User.objects.filter(is_active=True)
        user_data = []

        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.groups.filter(name='admin').exists(),
            }
            user_data.append(user_dict)

        data = {'users': user_data}
        return JsonResponse(data, safe=False)

# Admin CRUD operations
### Upload game image to static folder
"""
def upload_game_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        try:
            with open(f'static/images/{image.name}', 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    if request.method == 'PUT':
        image = request.FILES.get('image')
        try:
            with open(f'static/images/{image.name}', 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
"""
            
### Create, update and delete games
def game(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        displayName = request.POST.get('displayName')
        show = request.POST.get('show')
        show = show == 'on'
        
        try:
            game = Game.objects.create(name=name, displayName=displayName, show=show)
            game.save()
            log = Log.objects.create(actionPerformed=f' Crea juego: {name}', user=request.user)
            log.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    # Patch method needs testing
    if request.method == 'PATCH':
        id = request.POST.get('id')
        name = request.POST.get('name')
        displayName = request.POST.get('displayName')
        available = request.POST.get('available')
        show = request.POST.get('show')
        file_route = request.POST.get('file_route')
        try:
            game = Game.objects.get(id=id)
            game.name = name
            game.displayName = displayName
            game.available = available
            game.show = show
            game.file_route = file_route
            game.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    if request.method == 'DELETE':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body.decode('utf-8'))
            game_id = data.get('id')

            if game_id is not None:
                game = Game.objects.get(id=game_id)
                game.delete()
                log = Log.objects.create(actionPerformed=f' Elimina juego: {game.name}', user=request.user)
                log.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing or invalid id in request body'})
        except Game.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Game not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

### Create, update and delete students
def student(request):
    if request.method == 'DELETE':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body.decode('utf-8'))
            student_id = data.get('id')

            if student_id is not None:
                student = Student.objects.get(id=student_id)
                student.delete()
                log = Log.objects.create(actionPerformed=f' Elimina datos de estudiante: {student_id}', user=request.user)
                log.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing or invalid id in request body'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

### Create, update and delete plays
def play(request):
    if request.method == 'DELETE':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body.decode('utf-8'))
            play_id = data.get('id')

            if play_id is not None:
                play = Plays.objects.get(id=play_id)
                play.delete()
                log = Log.objects.create(actionPerformed=f' Elimina sesión de juego de: {play.student_id}', user=request.user)
                log.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing or invalid id in request body'})
        except Plays.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Play not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
### Create, update and delete users
def user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        is_admin = request.POST.get('is_admin')
        try:
            # First check if the user already exists, in which case verify that it is not active
            user = User.objects.filter(username=username)
            if user.exists():
                user = user.first()
                if user.is_active:
                    return JsonResponse({'status': 'error', 'message': 'User already exists'})
                else:
                    user.is_active = True
                    if is_admin == 'on':
                        admin_group = Group.objects.get(name='admin')
                        user.groups.add(admin_group)
                    user.save()
                    log = Log.objects.create(actionPerformed=f' Reactiva usuario: {username}', user=request.user)
                    log.save()
                    return JsonResponse({'status': 'success'})
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()

                # Add user to admin group if is_admin is True
                if is_admin == 'on':
                    admin_group = Group.objects.get(name='admin')
                    user.groups.add(admin_group)

            log = Log.objects.create(actionPerformed=f' Crea usuario: {username}', user=request.user)
            log.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    if request.method == 'PUT':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body.decode('utf-8'))
            id = data.get('id')
            user = User.objects.get(id=id)
            # Check if the email changed and if it changed, update it
            username = data.get('username')
            email = data.get('email')
            if user.email != email and email != '' and email != None:
                # Check if the email changed and if it is already in use
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'status': 'error', 'message': 'Email already in use'})
                user.email = email
                user.username = username
            # Check if the password changed and if it changed, update it
            password = data.get('password')
            if password != '' and password != None:
                user.set_password(password)
            # Check if the is_admin field changed and if it changed, update it
            is_admin = data.get('is_admin')
            if is_admin == True and is_admin != None:
                admin_group = Group.objects.get(name='admin')
                user.groups.add(admin_group)
            else:
                admin_group = Group.objects.get(name='admin')
                user.groups.remove(admin_group)
            user.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    if request.method == 'DELETE':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('id')

            if user_id is not None:
                # Deactivate the user instead of deleting it
                user = User.objects.get(id=user_id)
                user.is_active = False
                user.save()
                log = Log.objects.create(actionPerformed=f' Desactiva usuario: {user.username}', user=request.user)
                log.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing or invalid id in request body'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})