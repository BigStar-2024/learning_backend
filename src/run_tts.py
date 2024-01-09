from kb.models.content import Question

questions = Question.objects.all()
for question in questions:
    question.save_gtts()
