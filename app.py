import streamlit as st
import re
import random
from docx import Document
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(page_title="İmtahan Hazırlayıcı", page_icon="🧠")

def full_text(paragraph):
    return ''.join(run.text for run in paragraph.runs).strip()

def parse_docx(file):
    doc = Document(file)
    question_pattern = re.compile(r"^\s*\d+[\.\)]\s+")
    option_pattern = re.compile(r"^\s*[A-Ea-e]\)\s+(.*)")

    paragraphs = list(doc.paragraphs)
    i = 0
    question_blocks = []

    while i < len(paragraphs):
        text = full_text(paragraphs[i])
        if question_pattern.match(text):
            question_text = question_pattern.sub('', text)
            i += 1
            options = []
            while i < len(paragraphs):
                text = full_text(paragraphs[i])
                match = option_pattern.match(text)
                if match:
                    options.append(match.group(1).strip())
                    i += 1
                elif text and not question_pattern.match(text) and len(options) < 5:
                    options.append(text)
                    i += 1
                else:
                    break
            if len(options) == 5:
                question_blocks.append((question_text, options))
        else:
            i += 1
    return question_blocks

def create_shuffled_docx_and_answers(questions):
    new_doc = Document()
    answer_key = []

    for idx, (question, options) in enumerate(questions, start=1):
        new_doc.add_paragraph(f"{idx}) {question}")
        correct_answer = options[0]
        random.shuffle(options)

        for j, option in enumerate(options):
            letter = chr(ord('A') + j)
            new_doc.add_paragraph(f"{letter}) {option}")
            if option.strip() == correct_answer.strip():
                answer_key.append(f"{idx}) {letter}")
    return new_doc, answer_key

# --- İstifadəçi interfeysi ---
st.sidebar.title("🔧 Menyu")
menu = st.sidebar.radio("➡️ Zəhmət olmasa rejim seçin:", ["🎲 Sualları Qarışdır", "📝 İmtahan Rejimi"])

# 1️⃣ Sualları qarışdırma rejimi
if menu == "🎲 Sualları Qarışdır":
    st.title("🎲 Test Suallarını Qarışdır və Cavab Açarı Yarat")
    uploaded_file = st.file_uploader("📤 Word (.docx) sənədini seçin", type="docx")
    mode = st.radio("💡 Sualların sayı:", ["🔹 50 təsadüfi sual", "🔸 Bütün suallar"], index=0)

    if uploaded_file:
        questions = parse_docx(uploaded_file)
        if len(questions) < 5:
            st.error("❗ Faylda kifayət qədər uyğun sual tapılmadı.")
        else:
            selected = random.sample(questions, min(50, len(questions))) if "50" in mode else questions
            new_doc, answer_key = create_shuffled_docx_and_answers(selected)

            output_docx = BytesIO()
            new_doc.save(output_docx)
            output_docx.seek(0)

            output_answers = BytesIO()
            output_answers.write('\n'.join(answer_key).encode('utf-8'))
            output_answers.seek(0)

            st.success("✅ Qarışdırılmış sənədlər hazırdır!")
            st.download_button("📥 Qarışdırılmış Suallar (.docx)", output_docx, "qarisdirilmis_suallar.docx")
            st.download_button("📥 Cavab Açarı (.txt)", output_answers, "cavab_acari.txt")

# 2️⃣ İmtahan rejimi
elif menu == "📝 İmtahan Rejimi":
    st.title("📝 Özünü Sına: İmtahan Rejimi")
    uploaded_file = st.file_uploader("📤 İmtahan üçün Word (.docx) faylını seçin", type="docx")
    mode = st.radio("📌 Sual seçimi:", ["🔹 50 təsadüfi sual", "🔸 Bütün suallar"], index=0)

    if uploaded_file:
        questions = parse_docx(uploaded_file)
        if not questions:
            st.error("❗ Heç bir sual tapılmadı.")
        else:
            if "50" in mode:
                questions = random.sample(questions, min(50, len(questions)))

            # Yanlış cavablarla yenidən imtahan üçün xüsusi açar yoxdursa, əsas imtahan rejimi başlayır
            if "exam_mode" not in st.session_state:
                st.session_state.exam_mode = "main" # "main" və ya "retry"

            if "started" not in st.session_state:
                st.session_state.started = False
                st.session_state.questions = questions
                st.session_state.current = 0
                st.session_state.answers = []
                st.session_state.correct_answers = [opts[0] for _, opts in questions]
                st.session_state.start_time = None
                st.session_state.timer_expired = False

            if not st.session_state.started:
                st.info("📌 60 dəqiqə vaxtınız olacaq. Hazırsınızsa başlayın!")
                if st.button("🚀 Başla"):
                    st.session_state.started = True
                    st.session_state.start_time = datetime.now()
                    st.rerun()

            elif st.session_state.started:
                now = datetime.now()
                time_left = timedelta(minutes=60) - (now - st.session_state.start_time)
                if time_left.total_seconds() <= 0:
                    st.session_state.timer_expired = True

                if st.session_state.timer_expired:
                    st.warning("⏰ Vaxt bitdi! İmtahan sona çatdı.")
                    st.session_state.current = len(st.session_state.questions)
                else:
                    mins, secs = divmod(int(time_left.total_seconds()), 60)
                    st.info(f"⏳ Qalan vaxt: {mins} dəq {secs} san")

                idx = st.session_state.current
                total = len(st.session_state.questions)
                if idx < total:
                    qtext, options = st.session_state.questions[idx]
                    correct = options[0]
                    if f"shuffled_{idx}" not in st.session_state:
                        shuffled = options[:]
                        random.shuffle(shuffled)
                        st.session_state[f"shuffled_{idx}"] = shuffled
                    else:
                        shuffled = st.session_state[f"shuffled_{idx}"]

                    # Proqres çubuğu
                    st.progress((idx / total))

                    st.markdown(f"**{idx+1}) {qtext}**")
                    selected = st.radio("📌 Cavab seçin:", shuffled, key=f"answer_{idx}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("⬅️ Əvvəlki", disabled=idx == 0):
                            st.session_state.current -= 1
                            st.rerun()
                    with col2:
                        if st.button("🚩 Bitir"):
                            st.session_state.current = len(st.session_state.questions)
                            st.rerun()
                    with col3:
                        if st.button("➡️ Növbəti", disabled=(selected is None)):
                            if len(st.session_state.answers) <= idx:
                                st.session_state.answers.append(selected)
                                st.session_state.correct_answers[idx] = correct
                            else:
                                st.session_state.answers[idx] = selected
                                st.session_state.correct_answers[idx] = correct
                            st.session_state.current += 1
                            st.rerun()
                else:
                    st.success("🎉 İmtahan tamamlandı!")
                    score = sum(1 for a, b in zip(st.session_state.answers, st.session_state.correct_answers) if a == b)
                    total = len(st.session_state.questions)
                    percent = (score / total) * 100 if total > 0 else 0
                    st.markdown(f"### ✅ Nəticə: {score} düzgün cavab / {total} sual")
                    st.markdown(f"### 📈 Doğruluq faizi: **{percent:.2f}%**")
                    st.progress(score / total if total > 0 else 0)

                    with st.expander("📊 Detallı nəticələr"):
                        for i, (ua, ca, q) in enumerate(zip(st.session_state.answers, st.session_state.correct_answers, st.session_state.questions)):
                            status = "✅ Düzgün" if ua == ca else "❌ Səhv"
                            st.markdown(f"**{i+1}) {q[0]}**\n• Sənin cavabın: `{ua}`\n• Doğru cavab: `{ca}` → {status}")

                    # Yanlış cavab verilən sualları ayırırıq
                    wrong_questions = [
                        (q, opts)
                        for i, (ua, ca, (q, opts)) in enumerate(zip(st.session_state.answers, st.session_state.correct_answers, st.session_state.questions))
                        if ua != ca
                    ]

                    # Yanlış cavab verilən suallar varsa, yenidən imtahan düyməsi göstəririk
                    if wrong_questions and st.session_state.exam_mode == "main":
                        if st.button("🔄 Yanlış cavablandırılan sualları yenidən sınayın"):
                            #
