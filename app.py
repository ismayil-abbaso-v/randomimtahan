import streamlit as st
import re
import random
from docx import Document
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(page_title="İmtahan Hazırlayıcı", page_icon="📝")

# 🔧 Fayldan test suallarını oxuma funksiyası
def full_text(paragraph):
    return ''.join(run.text for run in paragraph.runs).strip()

def parse_docx(file):
    doc = Document(file)
    question_pattern = re.compile(r"^\s*\d+[.)]\s+")
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

# 🔧 Açıq sualları oxuma funksiyası (bilet rejimi üçün)
def parse_open_questions(file):
    doc = Document(file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    question_pattern = re.compile(r"^\s*\d+[.)]\s+")

    questions = []
    for p in paragraphs:
        if not question_pattern.match(p):
            questions.append(p)

    return questions
   
# 🌐 Sessiya idarəsi
if "page" not in st.session_state:
    st.session_state.page = "home"

# 🏠 Ana səhifə
if st.session_state.page == "home":
    st.title("📝 Testləri Qarışdır və Biliklərini Yoxla!")
    st.markdown("Zəhmət olmasa bir rejim seçin:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Özünü imtahan et"):
            st.session_state.page = "exam"
            st.rerun()
    with col2:
        if st.button("🎲 Sualları Qarışdır"):
            st.session_state.page = "shuffle"
            st.rerun()
    with col3:
        if st.button("🎫 Bilet İmtahanı"):
            st.session_state.page = "ticket"
            st.rerun()

# 📋 Əsas menyu
else:
    st.sidebar.title("🔧 Menyu")
    if st.sidebar.button("🏠 Ana Səhifəyə Qayıt"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.page = "home"
        st.rerun()

    menu = st.sidebar.radio("➡️ Rejimi dəyiş:", ["🎲 Sualları Qarışdır", "📝 Özünü İmtahan Et", "🎫 Bilet İmtahanı"],
        index=["shuffle", "exam", "ticket"].index(st.session_state.page))
    st.session_state.page = {"🎲 Sualları Qarışdır": "shuffle", "📝 Özünü İmtahan Et": "exam", "🎫 Bilet İmtahanı": "ticket"}[menu]


    # 1️⃣ Sualları qarışdır
    if st.session_state.page == "shuffle":
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

# 2️⃣ İmtahan rejimi (Hamısı bir səhifədə + qarışıq variantlar + vaxtölçən)
    elif st.session_state.page == "exam":
        st.title("📝 Özünü Sına: İmtahan Rejimi (60 dəqiqəlik)")

        uploaded_file = st.file_uploader("📤 İmtahan üçün Word (.docx) faylını seçin", type="docx")
        mode = st.radio("📌 Sual seçimi:", ["🔹 50 təsadüfi sual", "🔸 Bütün suallar"], index=0)

        if uploaded_file:
            questions = parse_docx(uploaded_file)
            if not questions:
                st.error("❗ Heç bir sual tapılmadı.")
            else:
                if "exam_started" not in st.session_state:
                    st.session_state.exam_started = False
                if "exam_submitted" not in st.session_state:
                    st.session_state.exam_submitted = False
                if "exam_start_time" not in st.session_state:
                    st.session_state.exam_start_time = None

                if not st.session_state.exam_started:
                    if st.button("🚀 İmtahana Başla"):
                        selected = random.sample(questions, min(50, len(questions))) if "50" in mode else questions

                        shuffled_questions = []
                        for q_text, opts in selected:
                            correct = opts[0]
                            shuffled = opts[:]
                            random.shuffle(shuffled)
                            shuffled_questions.append((q_text, shuffled, correct))

                        st.session_state.exam_questions = shuffled_questions
                        st.session_state.exam_answers = [""] * len(shuffled_questions)
                        st.session_state.exam_start_time = datetime.now()
                        st.session_state.exam_started = True
                        st.rerun()

                elif st.session_state.exam_started and not st.session_state.exam_submitted:
                    elapsed = datetime.now() - st.session_state.exam_start_time
                    remaining = timedelta(minutes=60) - elapsed
                    seconds_left = int(remaining.total_seconds())

                    if seconds_left <= 0:
                        st.warning("⏰ Vaxt bitdi! İmtahan tamamlandı.")
                        st.session_state.exam_submitted = True
                        st.rerun()
                    else:
                        mins, secs = divmod(seconds_left, 60)
                        st.info(f"⏳ Qalan vaxt: {mins} dəq {secs} san")

                        for i, (qtext, options, _) in enumerate(st.session_state.exam_questions):
                            st.markdown(f"**{i+1}) {qtext}**")
                            st.session_state.exam_answers[i] = st.radio(
    label="", options=options, key=f"q_{i}", label_visibility="collapsed"
)

                        if st.button("📤 İmtahanı Bitir"):
                            st.session_state.exam_submitted = True
                            st.rerun()

                elif st.session_state.exam_submitted:
                    st.success("🎉 İmtahan tamamlandı!")

                    correct_list = [correct for _, _, correct in st.session_state.exam_questions]
                    score = sum(1 for a, b in zip(st.session_state.exam_answers, correct_list) if a == b)
                    total = len(correct_list)
                    percent = (score / total) * 100

                    st.markdown(f"### ✅ Nəticə: {score} düzgün cavab / {total} sual")
                    st.markdown(f"<p style='font-size:16px;'>📈 Doğruluq faizi: <strong>{percent:.2f}%</strong></p>", unsafe_allow_html=True)
                    st.progress(score / total)

                    with st.expander("📊 Detallı nəticələr"):
                        for i, (ua, ca, (qtext, _, _)) in enumerate(zip(st.session_state.exam_answers, correct_list, st.session_state.exam_questions)):
                            status = "✅ Düzgün" if ua == ca else "❌ Səhv"
                            st.markdown(f"**{i+1}) {qtext}**\n• Sənin cavabın: `{ua}`\n• Doğru cavab: `{ca}` → {status}")

                    if st.button("🔁 Yenidən Başla"):
                        for key in ["exam_questions", "exam_answers", "exam_started", "exam_submitted", "exam_start_time"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                        
   # 3️⃣ Bilet İmtahanı (🎟️ düyməsi bir dəfəlik)
    elif st.session_state.page == "ticket":
        st.title("🎫 Bilet İmtahanı (Açıq suallar)")
        uploaded_file = st.file_uploader("📤 Bilet sualları üçün Word (.docx) faylı seçin", type="docx")

        if uploaded_file:
            questions = parse_open_questions(uploaded_file)
            if len(questions) < 5:
                st.error("❗ Kifayət qədər sual yoxdur (minimum 5 tələb olunur).")
            else:
                if "ticket_questions" not in st.session_state:
                    st.session_state.ticket_questions = []
                if "ticket_started" not in st.session_state:
                    st.session_state.ticket_started = False

                if not st.session_state.ticket_started:
                    if st.button("🎟️ Bilet Çək"):
                        st.session_state.ticket_questions = random.sample(questions, 5)
                        st.session_state.ticket_started = True

                if st.session_state.ticket_started:
                    st.success("✅ Hazır bilet sualları:")
                    for i, q in enumerate(st.session_state.ticket_questions, 1):
                        st.markdown(f"<p style='font-size:16px;'><strong>{i})</strong> {q}</p>", unsafe_allow_html=True)

                    st.markdown("---")
                    if st.button("🔁 Yenidən Bilet Çək"):
                        st.session_state.ticket_questions = random.sample(questions, 5)

