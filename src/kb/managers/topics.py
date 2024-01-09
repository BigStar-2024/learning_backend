from app.models import ActiveManager
from parler.managers import TranslatableManager, TranslatableQuerySet
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet


class TopicQuerySet(TranslatableQuerySet, TreeQuerySet):

    def as_manager(cls):
        # make sure creating managers from querysets works.
        manager = TopicManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager
    as_manager.queryset_only = True
    as_manager = classmethod(as_manager)


class TopicManager(ActiveManager, TreeManager, TranslatableManager):
    _queryset_class = TopicQuerySet
