from sqlalchemy.orm import joinedload

def get_monitor_with_user(db, monitor_id):
    return (
        db.query(Monitor)
        .options(joinedload(Monitor.user))  # load user along with monitor
        .filter(Monitor.id == monitor_id)
        .first()
    )
