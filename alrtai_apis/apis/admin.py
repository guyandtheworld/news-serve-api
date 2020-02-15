from django.contrib import admin
from .models.scenario import (
    Scenario,
    Bucket,
    BucketWeight,
    ModelDetails,
    BucketModel,
    Source,
)
from .models.users import User, Client, UserScenario

admin.site.register(Client)
admin.site.register(Scenario)
admin.site.register(User)
admin.site.register(UserScenario)
admin.site.register(Bucket)
admin.site.register(BucketWeight)
admin.site.register(ModelDetails)
admin.site.register(BucketModel)
admin.site.register(Source)

