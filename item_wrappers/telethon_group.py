import telethon
import telethon.tl.types as telethon_types
# from support.misc import datetime2str
from .. support.datetimefuncs import datetime2str
# from scraper_pipeline.item_wrappers.item import ProtoItem
from . item import ProtoItem

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_entity_category(entity):
    entity_type = type(entity)
    if entity_type == telethon_types.User:
        return "user"
    elif entity_type == telethon_types.Channel:
        if entity.megagroup:
            return "public_group"
        else:
            return "broadcast_channel"
    elif entity_type == telethon_types.Chat:
        return "private_group"
    else:
        return None

def get_entity_name(entity):
    """ Given a Telethon Entity object it returns the name of that entity """
    name = getattr(entity, "username", getattr(entity, "title", None))
    name = name if name is not None else telethon.utils.get_display_name(entity)
    return name



################################################################################
class TelethonGroupInfo(ProtoItem):
    def __init__(self, entity, url=None):
        ProtoItem.__init__(self)
        self.url = url
        self.date_format = DATE_FORMAT
        self.tz = "UTC"
        self._contents = self.extract_entity_info(entity)

    # def summary(self, format="", text_limit=20):
    #     return format.format(text_short=self._contents["text"][:text_limit], **self._contents)

    def __str__(self):
        return self.summary(format="{type} {id} {name}")
    # def __repr__(self):
    #     return "<TelethonGroupInfo OBJECT:  {}>".format(self.summary())

    def extract_entity_info(self, entity):
        info = {}
        info["id"] = entity.id
        info["time_created"] = datetime2str(entity.date, format=self.date_format, tz=self.tz)
        info["name"] = get_entity_name(entity)
        info["url"] = self.url

        info["is_private_group"] = False
        info["is_public_group"] = False
        info["is_broadcast_channel"] = False
        info["is_megagroup"] = False

        entity_category = get_entity_category(entity)
        info["type"] = entity_category
        if entity_category == "public_group":
            info["is_public_group"] = True
            info["is_megagroup"] = True
        elif entity_category == "broadcast_channel":
            info["is_broadcast_channel"] = True
        elif entity_category == "private_group":
            info["is_private_group"] = True
        return info
