from django.shortcuts import render, redirect
from .models import ClassicItem, CSQuestion
import random

# Create your views here.

def homepage(request):
    return render(request, 'game/homepage.html')

def classic_mode(request):
    # Za početak samo prikaz stranice s informacijom i linkom za igru
    return render(request, 'game/classic_mode.html')

def cs_mode(request):
    # Prikaz izbora težine
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty')
        if difficulty in ['easy', 'medium', 'hard']:
            request.session['cs_difficulty'] = difficulty
            request.session['cs_score'] = 0
            return redirect('cs_play')
    return render(request, 'game/cs_mode.html')

def cs_play(request):
    difficulty = request.session.get('cs_difficulty', None)
    if difficulty is None:
        return redirect('cs_mode')

    questions = list(CSQuestion.objects.filter(difficulty=difficulty))
    if not questions:
        return render(request, 'game/error.html', {'message': 'Nema pitanja za ovu težinu.'})

    question_id = request.session.get('cs_question_id')

    if request.method == 'POST':
        player_choice = request.POST.get('choice')
        question_id = request.session.get('cs_question_id')
        question = CSQuestion.objects.get(id=question_id)

        given_number = request.session.get('cs_given_number')
        correct_answer = int(question.correct_answer)

        if (player_choice == 'higher' and correct_answer > given_number) or \
           (player_choice == 'lower' and correct_answer < given_number):
            request.session['cs_score'] += 1
            message = 'Točno!'
        else:
            message = 'Netočno!'
            best_score = request.session.get('cs_best_score', 0)
            if request.session['cs_score'] > best_score:
                request.session['cs_best_score'] = request.session['cs_score']
            return render(request, 'game/cs_results.html', {
                'score': request.session['cs_score'],
                'best_score': request.session.get('cs_best_score', 0)
            })

    question = random.choice(questions)
    request.session['cs_question_id'] = question.id

    correct = int(question.correct_answer)  # <-- OBAVEZNO pretvori u int OVDJE
    offset = random.randint(1, max(1, int(abs(correct * 0.5))))
    if random.choice([True, False]):
        given_number = correct + offset
    else:
        given_number = max(0, correct - offset)

    if given_number == correct:
        given_number += 1

    request.session['cs_given_number'] = given_number

    return render(request, 'game/cs_play.html', {
        'question': question,
        'given_number': given_number,
        'score': request.session.get('cs_score', 0),
    })

