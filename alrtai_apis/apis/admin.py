from django.contrib import admin
from .models.scenario import Scenario, Bucket, BucketWeight
from .models.users import User, Client, UserScenario

admin.site.register(Client)
admin.site.register(Scenario)
admin.site.register(User)
admin.site.register(UserScenario)
admin.site.register(Bucket)
admin.site.register(BucketWeight)

