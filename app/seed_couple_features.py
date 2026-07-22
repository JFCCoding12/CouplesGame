from app.extensions import db
from app.models import CoupleQuestionnaire, CoupleQuestionnaireQuestion


def seed_couple_features():
    questionnaires = [
        {
            "title": "Relationship Check-In",
            "subtitle": "A short check-in about how things are going.",
            "emoji": "❤️",
            "primary_color": "#C94B4B",
            "secondary_color": "#4B134F",
            "sort_order": 1,
            "questions": [
                "What is one thing we are doing really well lately?",
                "What is one thing you wish we made more time for?",
                "What is something I did recently that made you feel loved?",
                "How can I support you better this week?",
                "What is one small thing we could improve together?"
            ],
        },
        {
            "title": "Future Us",
            "subtitle": "Dreams, goals, and where life is headed.",
            "emoji": "🌅",
            "primary_color": "#355C7D",
            "secondary_color": "#6C5B7B",
            "sort_order": 2,
            "questions": [
                "Where do you picture us one year from now?",
                "What is one goal you want us to work toward together?",
                "What kind of home or lifestyle do you imagine for us someday?",
                "What is one tradition you would like us to start?",
                "What are you most excited to experience together?"
            ],
        },
        {
            "title": "How Well Do You Know Me?",
            "subtitle": "Guess, compare, and laugh about the answers.",
            "emoji": "🎯",
            "primary_color": "#7F00FF",
            "secondary_color": "#E100FF",
            "sort_order": 3,
            "questions": [
                "What is my ideal lazy day?",
                "What food could I probably eat forever?",
                "What is something that instantly stresses me out?",
                "What is one thing I am secretly proud of?",
                "What is my favorite way to be comforted?"
            ],
        },
        {
            "title": "Appreciation Round",
            "subtitle": "Say the things that are easy to forget to say.",
            "emoji": "💌",
            "primary_color": "#C33764",
            "secondary_color": "#FF6B6B",
            "sort_order": 4,
            "questions": [
                "What is something you appreciate about me that you do not say enough?",
                "What is one way I make your life better?",
                "What is a little thing I do that means more than I realize?",
                "What is something about me that makes you proud?",
                "What is one memory with me that you are grateful for?"
            ],
        },
    ]

    for item in questionnaires:
        questionnaire = CoupleQuestionnaire.query.filter_by(
            title=item["title"]
        ).first()

        if not questionnaire:
            questionnaire = CoupleQuestionnaire(
                title=item["title"],
                subtitle=item["subtitle"],
                emoji=item["emoji"],
                primary_color=item["primary_color"],
                secondary_color=item["secondary_color"],
                sort_order=item["sort_order"],
                is_active=True,
                is_nsfw=False,
            )
            db.session.add(questionnaire)
            db.session.flush()

        for index, text in enumerate(item["questions"], start=1):
            exists = CoupleQuestionnaireQuestion.query.filter_by(
                questionnaire_id=questionnaire.id,
                text=text,
            ).first()

            if exists:
                continue

            db.session.add(
                CoupleQuestionnaireQuestion(
                    questionnaire_id=questionnaire.id,
                    text=text,
                    position=index,
                    is_required=True,
                )
            )

    db.session.commit()