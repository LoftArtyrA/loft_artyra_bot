from handlers.start import register_start_handlers
from handlers.order import register_order_handlers
from handlers.quiz import register_quiz_handlers
from handlers.referral import register_referral_handlers
from handlers.review import register_review_handlers
from handlers.tour import register_tour_handlers
from handlers.admin import register_admin_handlers

def register_all_handlers(dp):
    register_start_handlers(dp)
    register_order_handlers(dp)
    register_quiz_handlers(dp)
    register_referral_handlers(dp)
    register_review_handlers(dp)
    register_tour_handlers(dp)
    register_admin_handlers(dp)