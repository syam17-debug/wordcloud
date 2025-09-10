pip install wordcloud
import streamlit as st
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import PyPDF2
from docx import Document
import io
from langdetect import detect
from collections import Counter
import pandas as pd

# --- Text Extraction ---
def extract_text_from_pdf(file_bytes):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return " ".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        st.error(f"PDF error: {e}")
        return ""

def extract_text_from_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"DOCX error: {e}")
        return ""

# --- Word Cloud Generator ---
def generate_word_cloud(text, max_words, bg_color, width, height, extra_stopwords):
    all_stopwords = STOPWORDS.union(set(extra_stopwords.split()))
    wc = WordCloud(
        width=width,
        height=height,
        background_color=bg_color,
        stopwords=all_stopwords,
        collocations=False
    ).generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

    # Show word frequency table
    words = [word for word in text.lower().split() if word not in all_stopwords]
    freq = Counter(words)
    df = pd.DataFrame(freq.most_common(20), columns=["Word", "Frequency"])
    st.dataframe(df)

# --- Main App ---
def main():
    st.set_page_config(page_title="Unique Word Cloud App", layout="wide")
    st.title("🧠 Unique Word Cloud Generator")

    col1, col2 = st.columns([1, 2])

    with col1:
        input_mode = st.radio("Choose input mode:", ["Upload File", "Type Text"])
        uploaded_file = None
        raw_text = ""

        if input_mode == "Upload File":
            uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
            if uploaded_file:
                file_bytes = uploaded_file.getvalue()
                if uploaded_file.type == "application/pdf":
                    raw_text = extract_text_from_pdf(file_bytes)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    raw_text = extract_text_from_docx(file_bytes)
        else:
            raw_text = st.text_area("Enter your text here:", height=200)

        if raw_text:
            try:
                lang = detect(raw_text)
                st.markdown(f"🌐 Detected Language: *{lang.upper()}*")
            except:
                st.warning("Could not detect language.")

        st.subheader("🔧 Word Cloud Settings")
        max_words = st.slider("Max words", 50, 500, 150)
        bg_color = st.selectbox("Background color", ["white", "black", "lightblue", "lightgrey"])
        width = st.slider("Width", 300, 1000, 800)
        height = st.slider("Height", 300, 800, 400)
        extra_stopwords = st.text_input("Add custom stopwords (space-separated):", "")

    with col2:
        if raw_text.strip():
            st.subheader("☁ Generated Word Cloud")
            generate_word_cloud(raw_text, max_words, bg_color, width, height, extra_stopwords)
        else:
            st.info("Please upload a file or enter some text to begin.")

if __name__ == "__main__":
    main()
