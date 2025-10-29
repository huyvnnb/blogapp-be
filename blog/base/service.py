from typing import Any

from blog import db
from blog.exception import NotFound, ApiError


class CRUDTemplate:
    model = None

    @classmethod
    def create(cls, obj: Any):
        if isinstance(obj, dict):
            obj_instance = cls.model(**obj)
        else:
            obj_instance = obj

        db.session.add(obj_instance)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ApiError(message=str(e), status_code=500)

        return obj

    @classmethod
    def get_all(cls):
        objs = cls.model.query.all()
        return [obj.to_dict() for obj in objs]

    @classmethod
    def get(cls, obj_id: int):
        data = cls.model.query.get(obj_id)
        if not data:
            raise NotFound(message="Not found object")
        return data

    @classmethod
    def update(cls, obj: Any, data: dict):
        print(f"obj: {obj}")
        print(f"Data: {data}")
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ApiError(message=str(e), status_code=500)
        return obj.to_dict()

    @classmethod
    def delete(cls, obj: Any):
        db.session.delete(obj)
        db.session.commit()

