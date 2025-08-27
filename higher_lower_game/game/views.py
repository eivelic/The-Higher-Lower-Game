from django.shortcuts import render, redirect
from .models import ClassicItem, CSQuestion, ClassicLeaderboard, CSLeaderboard
from .forms import NicknameForm
import random

# ---------------------- NOVO: unos nadimka ----------------------
def nickname_input(request):
    if request.method == 'POST':
        form = NicknameForm(request.POST)
        if form.is_valid():
            request.session['nickname'] = form.cleaned_data['nickname']
            return redirect('homepage')
    else:
        form = NicknameForm()
    return render(request, 'game/nickname.html', {'form': form})

# ---------------------- NOVO: izmjena nadimka ----------------------   
def reset_nickname(request):
    if request.method == 'POST':
        request.session.pop('nickname', None)
        request.session.pop('score', None)
        request.session.pop('highscore', None)
        request.session.pop('item1_id', None)
        request.session.pop('item2_id', None)
        request.session.pop('cs_score', None)
        request.session.pop('cs_difficulty', None)
        request.session.pop('cs_question_id', None)
        request.session.pop('cs_given_number', None)
        
        return redirect('nickname_input')
    return redirect('homepage')

# ---------------------- IZMJENA: homepage ----------------------
def homepage(request):
    nickname = request.session.get('nickname')
    return render(request, 'game/index.html', {
        'nickname': nickname,
    })

# ---------------------- NOVO: leaderboard prikaz ----------------------
def classic_leaderboard(request):
    scores = ClassicLeaderboard.objects.order_by('-score')[:5]
    return render(request, 'game/classic_leaderboard.html', {'scores': scores})

def cs_leaderboard(request):
    easy_scores = CSLeaderboard.objects.filter(difficulty='easy').order_by('-score')[:5]
    medium_scores = CSLeaderboard.objects.filter(difficulty='medium').order_by('-score')[:5]
    hard_scores = CSLeaderboard.objects.filter(difficulty='hard').order_by('-score')[:5]

    return render(request, 'game/cs_leaderboard.html', {
        'easy_scores': easy_scores,
        'medium_scores': medium_scores,
        'hard_scores': hard_scores,
    })

# ---------------------- POSTOJEĆI: cs_mode ----------------------
def cs_mode(request):
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty')
        if difficulty in ['easy', 'medium', 'hard']:
            request.session['cs_difficulty'] = difficulty
            request.session['cs_score'] = 0
            return redirect('cs_play')
    return render(request, 'game/cs_mode.html')

# ---------------------- POSTOJEĆI: cs_play uz dodatak leaderboarda ----------------------
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
        question = CSQuestion.objects.get(id=question_id)
        given_number = request.session.get('cs_given_number')

        # koristi float da podržava i "1.5" i "10"
        correct_answer = float(question.correct_answer)

        if (player_choice == 'higher' and correct_answer > given_number) or \
           (player_choice == 'lower' and correct_answer < given_number):
            request.session['cs_score'] += 1
            message = 'Točno!'
        else:
            message = 'Netočno!'
            nickname = request.session.get('nickname', 'Anonimac')
            CSLeaderboard.objects.create(
                nickname=nickname,
                score=request.session['cs_score'],
                difficulty=difficulty
            )

            top_scores = CSLeaderboard.objects.filter(difficulty=difficulty).order_by('-score')
            if top_scores.count() > 5:
                for s in top_scores[5:]:
                    s.delete()

            return render(request, 'game/cs_results.html', {
                'score': request.session['cs_score'],
                'best_score': top_scores.first().score if top_scores else 0
            })

    question = random.choice(questions)
    request.session['cs_question_id'] = question.id

    correct = float(question.correct_answer)

    # ✅ offset radi i za decimale (zaokružujemo na cijeli broj jer randint ne prima float)
    offset = max(1, round(abs(correct * 0.15)))

    if random.choice([True, False]):
        given_number = correct + offset
    else:
        given_number = max(0, correct - offset)

    if given_number == correct:
        given_number += 1

    # spremi kao float (može se prikazati zaokruženo u template-u)
    request.session['cs_given_number'] = given_number

    return render(request, 'game/cs_play.html', {
        'question': question,
        'given_number': round(given_number, 2),  # ✅ prikaz max 2 decimale
        'score': request.session.get('cs_score', 0),
    })

# ---------------------- POSTOJEĆI: classic_mode uz dodatak leaderboarda ----------------------
def classic_mode(request):
    items = list(ClassicItem.objects.all())
    if len(items) < 2:
        return render(request, 'game/not_enough_items.html')

    if 'score' not in request.session:
        request.session['score'] = 0

    if 'highscore' not in request.session:
        request.session['highscore'] = 0

    if request.method == 'POST':
        guess = request.POST.get('guess')
        item1_id = request.session.get('item1_id')
        item2_id = request.session.get('item2_id')

        if not item1_id or not item2_id:
            return redirect('classic_mode')

        item1 = ClassicItem.objects.get(id=item1_id)
        item2 = ClassicItem.objects.get(id=item2_id)

        correct = False
        if guess == 'higher' and item2.monthly_searches > item1.monthly_searches:
            correct = True
        elif guess == 'lower' and item2.monthly_searches < item1.monthly_searches:
            correct = True

        if correct:
            request.session['score'] += 1
            if request.session['score'] > request.session['highscore']:
                request.session['highscore'] = request.session['score']

            request.session['item1_id'] = item2.id
            available_ids = list(ClassicItem.objects.exclude(id=item2.id).values_list('id', flat=True))
            new_item2_id = random.choice(available_ids)
            request.session['item2_id'] = new_item2_id

            return render(request, 'game/classic_mode.html', {
                'left_item': item2,
                'right_item': ClassicItem.objects.get(id=new_item2_id),
                'score': request.session['score'],
                'highscore': request.session['highscore'],
                'correct': True
            })

        else:
            final_score = request.session['score']
            nickname = request.session.get('nickname', 'Anonimac')
            ClassicLeaderboard.objects.create(nickname=nickname, score=final_score)

            top_scores = ClassicLeaderboard.objects.order_by('-score')
            if top_scores.count() > 5:
                for s in top_scores[5:]:
                    s.delete()

            request.session['score'] = 0
            request.session['item1_id'] = None
            request.session['item2_id'] = None
            request.session.modified = True

            return render(request, 'game/classic_results.html', {
                'score': final_score,
                'highscore': request.session['highscore']
            })

    if not request.session.get('item1_id') or not request.session.get('item2_id'):
        item1, item2 = random.sample(items, 2)
        request.session['item1_id'] = item1.id
        request.session['item2_id'] = item2.id
        request.session['score'] = 0

    else:
        item1 = ClassicItem.objects.get(id=request.session['item1_id'])
        item2 = ClassicItem.objects.get(id=request.session['item2_id'])

    return render(request, 'game/classic_mode.html', {
        'left_item': item1,
        'right_item': item2,
        'score': request.session['score'],
        'highscore': request.session['highscore']
    })


