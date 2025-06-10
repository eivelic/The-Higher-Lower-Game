from django.shortcuts import render, redirect
from .models import ClassicItem, CSQuestion
import random

# Create your views here.

def homepage(request):
    return render(request, 'game/homepage.html')

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

from django.shortcuts import render, redirect
from .models import ClassicItem
import random

def classic_mode(request):
    items = list(ClassicItem.objects.all())
    if len(items) < 2:
        return render(request, 'game/not_enough_items.html')

    # Inicijaliziraj score i high_score u session
    if 'score' not in request.session:
        request.session['score'] = 0
    if 'high_score' not in request.session:
        request.session['high_score'] = 0

    if request.method == 'POST':
        guess = request.POST.get('guess')
        item1_id = request.session.get('item1_id')
        item2_id = request.session.get('item2_id')

        if not item1_id or not item2_id:
            return redirect('classic_mode')  # Ponovno učitavanje ako nema itema

        item1 = ClassicItem.objects.get(id=item1_id)
        item2 = ClassicItem.objects.get(id=item2_id)

        correct = False
        if guess == 'higher' and item2.monthly_searches > item1.monthly_searches:
            correct = True
        elif guess == 'lower' and item2.monthly_searches < item1.monthly_searches:
            correct = True

        if correct:
            request.session['score'] += 1
            # Ažuriraj high_score ako je trenutni score veći
            if request.session['score'] > request.session['high_score']:
                request.session['high_score'] = request.session['score']
            # Pomakni se na iduću rundu
            request.session['item1_id'] = item2.id
            available_ids = list(ClassicItem.objects.exclude(id=item2.id).values_list('id', flat=True))
            new_item2_id = random.choice(available_ids)
            request.session['item2_id'] = new_item2_id

            item1 = item2
            item2 = ClassicItem.objects.get(id=new_item2_id)

            return render(request, 'game/classic_mode.html', {
                'left_item': item1,
                'right_item': item2,
                'score': request.session.get('score', 0),
                'high_score': request.session.get('high_score', 0),
                'correct': True  # → Pošalji flag za JS animaciju
            })

        else:
            final_score = request.session['score']
            # Ažuriraj high_score ako je trenutni score veći
            if final_score > request.session['high_score']:
                request.session['high_score'] = final_score
            request.session['score'] = 0
            request.session['item1_id'] = None
            request.session['item2_id'] = None
            request.session.modified = True
            return render(request, 'game/classic_results.html', {
                'score': final_score,
                'high_score': request.session.get('high_score', 0)
            })

    # GET zahtjev
    if not request.session.get('item1_id') or not request.session.get('item2_id'):
        item1, item2 = random.sample(items, 2)
        request.session['item1_id'] = item1.id
        request.session['item2_id'] = item2.id
        request.session['score'] = 0
    else:
        try:
            item1 = ClassicItem.objects.get(id=request.session['item1_id'])
            item2 = ClassicItem.objects.get(id=request.session['item2_id'])
        except ClassicItem.DoesNotExist:
            return redirect('classic_mode')

    return render(request, 'game/classic_mode.html', {
        'left_item': item1,
        'right_item': item2,
        'score': request.session.get('score', 0),
        'high_score': request.session.get('high_score', 0)
    })