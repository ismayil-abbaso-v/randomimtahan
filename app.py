
import streamlit as st
import re
import random
from docx import Document
from io import BytesIO

def parse_docx(file):
    doc = Document(file)
    sual_nusunesi = re.compile(r"^\s*\d+[\.\)]\s+")
    variant_nusunesi = re.compile(r"^\s*[A-Ea-e]\)\s+(.*)")

    paragraphlar = list(doc.paragraphs)
    i = 0
    sual_bloklari = []

    while i < len(paragraphlar):
        metn = paragraphlar[i].text.strip()

        if sual_nusunesi.match(metn):
            sual_metni = sual_nusunesi.sub('', metn)
            i += 1

            variantlar = []
            while i < len(paragraphlar):
                text = paragraphlar[i].text.strip()

                uygun = variant_nusunesi.match(text)
                if uygun:
                    variantlar.append(uygun.group(1).strip())
                    i += 1
                elif text and not sual_nusunesi.match(text) and len(variantlar) < 5:
                    variantlar.append(text)
                    i += 1
                else:
                    break

            if len(variantlar) == 5:
                sual_bloklari.append((sual_metni, variantlar))
        else:
            i += 1

    return sual_bloklari

def create_shuffled_docx_and_answers(suallar):
    yeni_doc = Document()
    cavablar = []

    for idx, (sual_metni, variantlar) in enumerate(suallar, start=1):
        yeni_doc.add_paragraph(f"{idx}) {sual_metni}")

        dogru_cavab_mətni = variantlar[0]  # A) həmişə doğru idi
        random.shuffle(variantlar)

        for j, variant in enumerate(variantlar):
            herf = chr(ord('A') + j)
            yeni_doc.add_paragraph(f"{herf}) {variant}")
            if variant.strip() == dogru_cavab_mətni.strip():
                cavablar.append(f"{idx}) {herf}")

    return yeni_doc, cavablar

# Streamlit interfeys
st.set_page_config(page_title="Test Qarışdırıcı", page_icon="📄")
st.title("📄 Word test suallarını qarışdır")
st.markdown("""
Yüklə `.docx` sənədini → İstədiyin rejimi seç:
- Bütün sualların variantları qarışdırılsın
- Yalnız 50 təsadüfi sual seçilsin

Variantlar qarışdırılır, cavab siyahısı çıxarılır ✅
""")

uploaded_file = st.file_uploader("Word (.docx) sənədini seç", type="docx")
mode = st.radio("Rejim seç:", ["50 sual", "Bütün suallar"], index=0)

if uploaded_file:
    suallar = parse_docx(uploaded_file)
    if len(suallar) < 5:
        st.error("Faylda kifayət qədər uyğun sual tapılmadı. Formatı yoxla.")
    else:
        if mode == "50 sual":
            secilmis = random.sample(suallar, min(50, len(suallar)))
        else:
            secilmis = suallar

        yeni_doc, cavablar = create_shuffled_docx_and_answers(secilmis)

        # Yeni .docx fayl
        output_docx = BytesIO()
        yeni_doc.save(output_docx)
        output_docx.seek(0)

        # Cavab siyahısı
        output_answers = BytesIO()
        output_answers.write('\n'.join(cavablar).encode('utf-8'))
        output_answers.seek(0)

        st.success("✅ Sənədlər hazırdır!")

        st.download_button("📥 Qarışdırılmış suallar (.docx)", data=output_docx, file_name="qarisdirilmis_suallar.docx")
        st.download_button("📥 Cavab açarı (.txt)", data=output_answers, file_name="cavablar.txt")
