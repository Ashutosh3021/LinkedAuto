from models import (
    db, Config, Post, Log, ConnectionJob,
    LinkedInCredential, ConnectionConfiguration,
    LinkedInProfile, DailyConnectionStats, AIProvider,
    LinkedInAppCredentials
)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class CRUDHelper:
    @staticmethod
    def create(model, **kwargs):
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    @staticmethod
    def get(model, id):
        return model.query.get(id)
    
    @staticmethod
    def get_all(model, order_by=None):
        query = model.query
        if order_by is not None:
            query = query.order_by(order_by)
        return query.all()
    
    @staticmethod
    def update(model, id, **kwargs):
        instance = model.query.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db.session.commit()
        return instance
    
    @staticmethod
    def delete(model, id):
        instance = model.query.get(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False

class ConfigHelper(CRUDHelper):
    @staticmethod
    def get_by_key(key):
        return Config.query.filter_by(key=key).first()
    
    @staticmethod
    def set_value(key, value):
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = value
            db.session.commit()
        else:
            config = Config(key=key, value=value)
            db.session.add(config)
            db.session.commit()
        return config

class PostHelper(CRUDHelper):
    @staticmethod
    def get_by_status(status):
        return Post.query.filter_by(status=status).all()

class LogHelper(CRUDHelper):
    @staticmethod
    def get_by_level(level, limit=100):
        return Log.query.filter_by(level=level).order_by(Log.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent(limit=100):
        return Log.query.order_by(Log.created_at.desc()).limit(limit).all()

class ConnectionJobHelper(CRUDHelper):
    @staticmethod
    def get_by_status(status):
        return ConnectionJob.query.filter_by(status=status).all()
