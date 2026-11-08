from flask import Flask, jsonify, render_template, request, session
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deploying")

GAMES = [
    {"id": "guess", "title": "الرقم السري", "icon": "🔢", "description": "اعثر على الرقم المخفي بين 1 و20."},
    {"id": "rps", "title": "حجر ورقة مقص", "icon": "✊", "description": "تحدَّ الكمبيوتر في لعبة كلاسيكية."},
    {"id": "xo", "title": "إكس أو", "icon": "⭕", "description": "كوّن صفاً من ثلاثة رموز قبل الكمبيوتر."},
    {"id": "quiz", "title": "اختبار المعلومات", "icon": "🧠", "description": "أجب عن خمسة أسئلة متنوعة."},
    {"id": "hangman", "title": "خمن الكلمة", "icon": "🔤", "description": "اكشف الكلمة حرفاً بحرف قبل نفاد المحاولات."},
    {"id": "math", "title": "تحدي الحساب", "icon": "➕", "description": "حل خمس مسائل حسابية بأسرع ما يمكنك."},
    {"id": "sequence", "title": "أكمل النمط", "icon": "🧩", "description": "اكتشف الرقم التالي في المتتالية."},
    {"id": "truefalse", "title": "صح أم خطأ", "icon": "✅", "description": "اختبر معلوماتك في خمس جولات سريعة."},
    {"id": "scramble", "title": "الكلمة المبعثرة", "icon": "🔀", "description": "رتب الحروف لتكتشف الكلمة الصحيحة."},
    {"id": "blackjack", "title": "21 المصغرة", "icon": "🃏", "description": "اقترب من 21 دون أن تتجاوزها."},
]

QUESTIONS = [
    ("ما عاصمة المغرب؟", ["الرباط", "فاس", "مراكش"], 0),
    ("كم عدد ألوان قوس قزح؟", ["خمسة", "سبعة", "تسعة"], 1),
    ("ما أكبر كوكب في المجموعة الشمسية؟", ["الأرض", "زحل", "المشتري"], 2),
    ("كم يساوي 6 × 7؟", ["42", "36", "48"], 0),
    ("ما الحيوان المعروف بسفينة الصحراء؟", ["الحصان", "الجمل", "الفيل"], 1),
    ("ما اللغة المستخدمة لتنسيق صفحات الويب؟", ["HTML", "CSS", "SQL"], 1),
    ("كم عدد أيام الأسبوع؟", ["ستة", "سبعة", "ثمانية"], 1),
]
WORDS = ["مدرسة", "حديقة", "حاسوب", "برتقال", "نافذة", "مكتبة", "طائرة", "قمر"]
FACTS = [
    ("الشمس نجم.", True), ("للمثلث أربعة أضلاع.", False),
    ("الماء يتجمد عند صفر درجة مئوية.", True), ("الأخطبوط له ستة أذرع.", False),
    ("الأرض تدور حول الشمس.", True), ("اللغة العربية تكتب من اليسار إلى اليمين.", False),
    ("للعنكبوت ثماني أرجل.", True),
]


def start_game(game_id):
    if game_id == "guess":
        return {"answer": random.randint(1, 20), "tries": 0, "message": "اختر رقماً من 1 إلى 20."}
    if game_id == "rps":
        return {"rounds": 0, "score": 0, "message": "اختر حركتك!"}
    if game_id == "xo":
        return {"board": [""] * 9, "message": "أنت X. اختر خانة فارغة."}
    if game_id == "quiz":
        questions = random.sample(QUESTIONS, 5)
        return {"questions": questions, "index": 0, "score": 0, "message": questions[0][0]}
    if game_id == "hangman":
        word = random.choice(WORDS)
        return {"word": word, "guessed": [], "wrong": 0, "message": "اكتب حرفاً واحداً لتخمين الكلمة."}
    if game_id == "math":
        return new_math_round(0, 0)
    if game_id == "sequence":
        start = random.randint(1, 8)
        step = random.randint(2, 6)
        return {"answer": start + step * 4, "sequence": [start + step * i for i in range(4)], "message": "ما الرقم التالي في النمط؟"}
    if game_id == "truefalse":
        facts = random.sample(FACTS, 5)
        return {"facts": facts, "index": 0, "score": 0, "message": facts[0][0]}
    if game_id == "scramble":
        word = random.choice(WORDS)
        return {"word": word, "scrambled": "".join(random.sample(list(word), len(word))), "message": "اكتب الكلمة الصحيحة."}
    if game_id == "blackjack":
        player = [random.randint(1, 10), random.randint(1, 10)]
        dealer = [random.randint(1, 10), random.randint(1, 10)]
        return {"player": player, "dealer": dealer, "finished": False, "message": "اسحب ورقة أو قف."}
    return None


def new_math_round(index, score):
    a, b = random.randint(2, 15), random.randint(2, 12)
    op = random.choice(["+", "−", "×"])
    answer = a + b if op == "+" else a - b if op == "−" else a * b
    return {"index": index, "score": score, "answer": answer, "message": f"كم يساوي {a} {op} {b}؟"}


def game_view(game_id, data):
    view = {"message": data.get("message", ""), "finished": data.get("finished", False), "input_type": "buttons", "options": [], "display": "", "score": None}
    if game_id == "guess":
        view.update(input_type="number", placeholder="رقم من 1 إلى 20", display=f"المحاولات: {data['tries']}")
    elif game_id == "rps":
        view.update(options=[{"value": x, "label": label} for x, label in [("rock", "✊ حجر"), ("paper", "✋ ورقة"), ("scissors", "✌️ مقص")]], display=f"الجولات: {data['rounds']} · انتصاراتك: {data['score']}", finished=data["rounds"] >= 5, message="انتهت اللعبة! أعد اللعب." if data["rounds"] >= 5 else data["message"])
    elif game_id == "xo":
        view.update(input_type="grid", options=[{"value": str(i), "label": value or "·"} for i, value in enumerate(data["board"])], finished=data.get("finished", False))
    elif game_id == "quiz":
        idx = data["index"]
        if idx < len(data["questions"]):
            q = data["questions"][idx]
            view.update(message=data.get("message", q[0]), options=[{"value": str(i), "label": answer} for i, answer in enumerate(q[1])], display=f"السؤال {idx + 1} من 5 · النقاط: {data['score']}")
        else:
            view.update(finished=True, message=f"انتهى الاختبار! نتيجتك {data['score']} من 5.", display="")
    elif game_id == "hangman":
        shown = " ".join(ch if ch in data["guessed"] else "＿" for ch in data["word"])
        view.update(input_type="text", placeholder="اكتب حرفاً", display=f"الكلمة: {shown}　 المحاولات الخاطئة: {data['wrong']} من 6", finished=data.get("finished", False))
    elif game_id == "math":
        view.update(input_type="number", placeholder="اكتب الناتج", display=f"المسألة {min(data['index'] + 1, 5)} من 5 · النقاط: {data['score']}", finished=data.get("finished", False))
    elif game_id == "sequence":
        view.update(input_type="number", placeholder="الرقم التالي", display="، ".join(map(str, data["sequence"])) + "، ؟", finished=data.get("finished", False))
    elif game_id == "truefalse":
        idx = data["index"]
        if idx < len(data["facts"]):
            view.update(message=data.get("message", data["facts"][idx][0]), options=[{"value": "true", "label": "صح"}, {"value": "false", "label": "خطأ"}], display=f"الجولة {idx + 1} من 5 · النقاط: {data['score']}")
        else:
            view.update(finished=True, message=f"انتهت اللعبة! نتيجتك {data['score']} من 5.", display="")
    elif game_id == "scramble":
        view.update(input_type="text", placeholder="اكتب الكلمة", display=f"الحروف: {data['scrambled']}", finished=data.get("finished", False))
    elif game_id == "blackjack":
        p_total = sum(data["player"])
        view.update(display=f"أوراقك: {' + '.join(map(str, data['player']))} = {p_total} · أوراق الموزع: {' + '.join(map(str, data['dealer'][:1]))} + ؟", finished=data["finished"], options=[] if data["finished"] else [{"value": "hit", "label": "🃏 اسحب"}, {"value": "stand", "label": "✋ قف"}])
    return view


def take_turn(game_id, data, action):
    if game_id == "guess":
        try: guess = int(action)
        except (ValueError, TypeError): return data
        if not 1 <= guess <= 20: data["message"] = "اختر رقماً بين 1 و20."; return data
        data["tries"] += 1
        if guess == data["answer"]: data.update(finished=True, message=f"أحسنت! وجدت الرقم بعد {data['tries']} محاولات.")
        elif data["tries"] >= 6: data.update(finished=True, message=f"انتهت المحاولات! الرقم كان {data['answer']}.")
        else: data["message"] = "الرقم أكبر من تخمينك." if guess < data["answer"] else "الرقم أصغر من تخمينك."
    elif game_id == "rps":
        if action not in ("rock", "paper", "scissors") or data["rounds"] >= 5: return data
        bot = random.choice(["rock", "paper", "scissors"]); data["rounds"] += 1
        if action == bot: result = "تعادل!"
        elif (action, bot) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]: data["score"] += 1; result = "فزت بهذه الجولة!"
        else: result = "فاز الكمبيوتر بهذه الجولة."
        data["message"] = f"{result} الكمبيوتر اختار {dict(rock='حجر', paper='ورقة', scissors='مقص')[bot]}."
    elif game_id == "xo":
        if data.get("finished") or not str(action).isdigit(): return data
        i = int(action); board = data["board"]
        if not 0 <= i < 9 or board[i]: return data
        board[i] = "X"
        if winner(board, "X"): data.update(finished=True, message="مبروك، فزت! 🏆"); return data
        empty = [j for j, v in enumerate(board) if not v]
        if not empty: data.update(finished=True, message="تعادل! أعد اللعب."); return data
        board[random.choice(empty)] = "O"
        if winner(board, "O"): data.update(finished=True, message="فاز الكمبيوتر. حاول مرة أخرى!")
        elif not any(not v for v in board): data.update(finished=True, message="تعادل! أعد اللعب.")
        else: data["message"] = "دورك الآن!"
    elif game_id == "quiz":
        idx = data["index"]
        if idx >= 5 or not str(action).isdigit(): return data
        if int(action) == data["questions"][idx][2]: data["score"] += 1; data["message"] = "إجابة صحيحة! 🌟"
        else: data["message"] = f"ليست الإجابة الصحيحة؛ الجواب هو: {data['questions'][idx][1][data['questions'][idx][2]]}."
        data["index"] += 1
        if data["index"] >= 5: data["finished"] = True; data["message"] = f"انتهى الاختبار! نتيجتك {data['score']} من 5."
        else: data["next_message"] = data["questions"][data["index"]][0]
    elif game_id == "hangman":
        letter = str(action).strip()[:1]
        if not letter or data.get("finished"): return data
        if letter not in data["guessed"]:
            data["guessed"].append(letter)
            if letter not in data["word"]: data["wrong"] += 1
        if all(ch in data["guessed"] for ch in data["word"]): data.update(finished=True, message=f"رائع! الكلمة هي {data['word']}.")
        elif data["wrong"] >= 6: data.update(finished=True, message=f"انتهت المحاولات! الكلمة هي {data['word']}.")
        else: data["message"] = "حرف صحيح!" if letter in data["word"] else "هذا الحرف غير موجود."
    elif game_id == "math":
        try: answer = int(action)
        except (ValueError, TypeError): return data
        if answer == data["answer"]: data["score"] += 1; data["message"] = "صحيح! 🎉"
        else: data["message"] = f"الإجابة الصحيحة هي {data['answer']}."
        data["index"] += 1
        if data["index"] >= 5: data.update(finished=True, message=f"انتهى التحدي! نتيجتك {data['score']} من 5.")
        else:
            next_data = new_math_round(data["index"], data["score"]); data.update(next_data)
    elif game_id == "sequence":
        try: answer = int(action)
        except (ValueError, TypeError): return data
        data.update(finished=True, message="إجابة صحيحة! أحسنت. 🎉" if answer == data["answer"] else f"ليست صحيحة؛ الرقم التالي هو {data['answer']}.")
    elif game_id == "truefalse":
        idx = data["index"]
        if idx >= 5 or action not in ("true", "false"): return data
        if (action == "true") == data["facts"][idx][1]: data["score"] += 1; data["message"] = "إجابة صحيحة! ✅"
        else: data["message"] = "إجابة خاطئة. ❌"
        data["index"] += 1
        if data["index"] >= 5: data["finished"] = True; data["message"] = f"انتهت اللعبة! نتيجتك {data['score']} من 5."
        else: data["next_message"] = data["facts"][data['index']][0]
    elif game_id == "scramble":
        if data.get("finished"): return data
        if str(action).strip() == data["word"]: data.update(finished=True, message="أحسنت! رتبت الكلمة بشكل صحيح. 🎉")
        else: data["message"] = "ليست صحيحة، حاول مرة أخرى!"
    elif game_id == "blackjack":
        if data["finished"]: return data
        if action == "hit":
            data["player"].append(random.randint(1, 10))
            if sum(data["player"]) > 21: data.update(finished=True, message=f"تجاوزت 21! مجموعك {sum(data['player'])}. خسرت الجولة.")
            else: data["message"] = "ورقة جيدة! اسحب أو قف."
        elif action == "stand":
            while sum(data["dealer"]) < 17: data["dealer"].append(random.randint(1, 10))
            p, d = sum(data["player"]), sum(data["dealer"])
            result = "تعادل!" if p == d else "فزت! 🎉" if d > 21 or p > d else "فاز الموزع."
            data.update(finished=True, message=f"{result} مجموعك {p} ومجموع الموزع {d}.")
    return data


def winner(board, mark):
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    return any(all(board[i] == mark for i in line) for line in lines)


@app.get("/")
def index():
    return render_template("index.html", games=GAMES)


@app.post("/api/start")
def api_start():
    game_id = request.json.get("game_id", "")
    if game_id not in {game["id"] for game in GAMES}: return jsonify({"error": "اللعبة غير موجودة"}), 404
    games = session.get("games", {})
    games[game_id] = start_game(game_id)
    session["games"] = games
    return jsonify(game_view(game_id, games[game_id]))


@app.post("/api/action")
def api_action():
    payload = request.get_json(silent=True) or {}
    game_id, action = payload.get("game_id", ""), payload.get("action", "")
    games = session.get("games", {})
    if game_id not in {game["id"] for game in GAMES} or game_id not in games:
        return jsonify({"error": "ابدأ اللعبة أولاً"}), 400
    games[game_id] = take_turn(game_id, games[game_id], action)
    if "next_message" in games[game_id]:
        games[game_id]["message"] = games[game_id].pop("next_message")
    session["games"] = games
    return jsonify(game_view(game_id, games[game_id]))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
