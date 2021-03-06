#!/usr/bin/env python
from .base import MokaModel
from .schema import MenuSchema


class Menu(MokaModel):
    collection_name = 'menus'
    default_get_attr = 'translations.language'
    Schema = MenuSchema

    @classmethod
    def get(cls, db, value, raw=False):
        return cls.find(db, {cls.default_get_attr: value}, raw_=raw)
