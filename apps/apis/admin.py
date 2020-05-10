from django.contrib import admin
from .models.scenario import (
    Scenario,
    Bucket,
    BucketWeight,
    ModelDetail,
    BucketModel,
    Source,
    Keywords
)

from .models.users import (
    DashUser,
    Client,
    UserScenario,
    Portfolio,
)

from .models.entity import (
    Entity,
    LastScrape,
    ScrapeSource,
    StoryEntityRef,
    StoryEntityMap,
    EntityType
)

from .models.story import (
    Story,
    BucketScore,
    EntityScore,
    StoryBody,
    StorySentiment
)


admin.site.register(Client)
admin.site.register(Scenario)
admin.site.register(DashUser)
admin.site.register(UserScenario)
admin.site.register(Bucket)
admin.site.register(BucketWeight)
admin.site.register(ModelDetail)
admin.site.register(BucketModel)
admin.site.register(Source)
admin.site.register(Portfolio)
admin.site.register(Entity)
admin.site.register(LastScrape)
admin.site.register(ScrapeSource)
admin.site.register(Story)
admin.site.register(BucketScore)
admin.site.register(EntityScore)
admin.site.register(StoryBody)
admin.site.register(StorySentiment)
admin.site.register(StoryEntityRef)
admin.site.register(StoryEntityMap)
admin.site.register(EntityType)
admin.site.register(Keywords)
