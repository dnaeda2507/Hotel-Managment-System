
# Sadece checkout temizlik util fonksiyonu bırakıldı
def create_checkout_cleaning_task(room_id: int, db):
    from app.agents.review_langgraph.langgraph_checkout_tools import create_cleaning_task_for_checkout
    return create_cleaning_task_for_checkout(room_id, db)