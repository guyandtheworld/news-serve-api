from django.contrib import admin
from .models.scenario import Scenario
from .models.users import User, Client, UserScenario

admin.site.register(Client)
admin.site.register(Scenario)
admin.site.register(User)
admin.site.register(UserScenario)

