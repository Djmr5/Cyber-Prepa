from django.db import models
from django.utils import timezone


class Student(models.Model):
    """Modelo de estudiante
    Matricula, unica
    Nombre, opcional
    Booleano de si se le olvido su credencial
    Hash de biometricos
    
    _get_played_today: Regresa el numero de juegos que jugo el dia de hoy
    _get_weekly_plays: Regresa el numero de juegos que jugo en la semana
    _get_sanctions_number: Regresa el numero de sanciones que tiene actualmente
    """

    id = models.CharField(primary_key=True, max_length=9)
    name = models.CharField(max_length=100, blank=True)
    forgoten_id = models.BooleanField(default=False)
    hash = models.CharField(max_length=1000, null=False, blank=False)

    def _get_played_today(self):
        today = timezone.now().date()
        return Play.objects.filter(student=self, time__date=today).count()

    def _get_weekly_plays(self):
        today = timezone.now().date()
        # Start of the week (Monday)
        start_of_week = today - timezone.timedelta(days=today.weekday())
        # End of the week (Sunday)
        end_of_week = start_of_week + timezone.timedelta(days=6)
        return Play.objects.filter(student=self, time__date__range=[start_of_week, end_of_week]).count()
    
    def _get_sanctions_number(self):
        return Sanction.objects.filter(student=self, end_time__gte=timezone.now()).count()

    def __str__(self):
        return self.id


class Game(models.Model):
    """Modelo de juegos
    Nombre, unico
    Booleano de si se muestra en la lista de juegos (Todavía se puede jugar o no)
    Fecha y hora en que el primer estudiante comenzó a jugar
    Ruta de la imagen del juego
    
    _get_plays: Regresa todos los juegos que se han jugado de este juego
    """
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    show = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    file_route = models.CharField(default='assets/games_cards/game.png', max_length=255)

    def _get_plays(self):
        return Play.objects.filter(game=self, ended=False)
    
    def _end_all_plays(self):
        plays = self._get_plays()
        for play in plays:
            play.ended = True
            play.save()

    def __str__(self):
        return f"{self.name} - {self.start_time}"


class Play(models.Model):
    """Modelo de juegos
    Relacion al estudiante que jugo
    Relacion al juego que se jugo
    Booleano de si terminó su juego y lo regresó
    Fecha y hora en que jugó
    """
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=False, blank=False)
    game = models.ForeignKey(Game, on_delete=models.PROTECT, null=False, blank=False)
    ended = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.game} - {self.time}"


class Sanction(models.Model):
    """Modelo de sanciones
    Causa de la sancion, escrita por el usuario
    Relacion a la play en la que se dio la sancion, puede ser null/blank
    Relacion al estudiante que esta siendo sancionado
    Fecha y hora en que se inicia la sancion
    Fecha y hora en que se termina la sancion
    """
    cause = models.CharField(max_length=255, null=False, blank=False)
    play = models.ForeignKey(Play, on_delete=models.PROTECT, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=False, blank=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return f"{self.student} - {self.start_time} - {self.end_time}"
