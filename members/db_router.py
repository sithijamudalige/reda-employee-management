# Create this file: members/db_router.py

class AttendanceRouter:
    """
    A router to control database operations for Attendance model.
    Routes Attendance to Access database, all other models to default database.
    """
    
    def db_for_read(self, model, **hints):
        """Route reads for Attendance to Access database"""
        if model._meta.app_label == 'members' and model.__name__ == 'Attendance':
            return 'access_db'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Route writes for Attendance to Access database"""
        if model._meta.app_label == 'members' and model.__name__ == 'Attendance':
            return 'access_db'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both models are in the same database"""
        if obj1._meta.app_label == 'members' and obj2._meta.app_label == 'members':
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control which database gets migrations.
        Attendance migrations go to access_db, others to default.
        """
        if model_name == 'attendance':
            return db == 'access_db'
        elif app_label == 'members':
            return db == 'default'
        return None