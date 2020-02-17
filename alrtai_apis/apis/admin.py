from django.contrib import admin
from .models.scenario import (
    Scenario,
    Bucket,
    BucketWeight,
    ModelDetail,
    BucketModel,
    Source,
)

from .models.users import (
    User,
    Client,
    UserScenario,
    Portfolio,
)

from .models.entity import (
    Entity,
    Alias,
    LastScraped,
    ScrapeSource,
)

from .models.story import (
    BucketScore,
    EntityScore,
)


admin.site.register(Client)
admin.site.register(Scenario)
admin.site.register(User)
admin.site.register(UserScenario)
admin.site.register(Bucket)
admin.site.register(BucketWeight)
admin.site.register(ModelDetail)
admin.site.register(BucketModel)
admin.site.register(Source)
admin.site.register(Portfolio)
admin.site.register(Entity)
admin.site.register(Alias)
admin.site.register(LastScraped)
admin.site.register(ScrapeSource)
admin.site.register(BucketScore)
admin.site.register(EntityScore)
