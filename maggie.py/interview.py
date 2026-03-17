import streamlit as st
import random
import pandas as pd
import speech_recognition as sr
import io
import tempfile
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Placement Interview Simulator")

st.title("AI Placement Interview Simulator")

role = st.selectbox(
"Select Job Role",
["Software Developer","Data Analyst","AI Engineer","Web Developer"]
)
questions_db = {

"Software Developer":[
"What is object oriented programming?",
"What is inheritance?",
"What is polymorphism?",
"What is version control?",
"What is debugging?"
],

"Data Analyst":[
"What is data analysis?",
"What is data cleaning?",
"What is data visualization?",
"What is exploratory data analysis?",
"What is data preprocessing?"
],

"AI Engineer":[
"What is machine learning?",
"What is deep learning?",
"What is neural network?",
"What is supervised learning?",
"What is artificial intelligence?"
],

"Web Developer":[
"What is HTML?",
"What is CSS?",
"What is JavaScript?",
"What is responsive design?",
"What is frontend and backend?"
]

}
def generate_questions(role):

    q = ["Please introduce yourself"]

    q += random.sample(questions_db[role],4)

    return q
def speak(text):

    tts = gTTS(text)

    filename="question.mp3"

    tts.save(filename)

    audio_file=open(filename,"rb")

    st.audio(audio_file.read())
def speech_to_text(audio_bytes):

    try:

        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

        temp_wav = tempfile.NamedTemporaryFile(delete=False,suffix=".wav")

        audio_segment.export(temp_wav.name,format="wav")

        recognizer = sr.Recognizer()

        with sr.AudioFile(temp_wav.name) as source:

            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

    except:

        text="Could not recognize speech"

    return text


# -------------------------
# EVALUATE ANSWER
# -------------------------

def evaluate_answer(answer,question):

    tokens = answer.lower().split()

    length_score = min(len(tokens)/25,1)

    vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform([answer,question])

    similarity = cosine_similarity(tfidf[0:1],tfidf[1:2])[0][0]

    score = (length_score + similarity)/2

    return round(score*10,2)


# -------------------------
# FEEDBACK
# -------------------------

def generate_feedback(score):

    if score >= 8:

        good = "Excellent explanation."

        missing = "Very few concepts missing."

    elif score >= 6:

        good = "Good answer."

        missing = "Add examples and deeper explanation."

    elif score >= 4:

        good = "Basic understanding present."

        missing = "Technical explanation missing."

    else:

        good = "Answer too short."

        missing = "Concept explanation missing."

    suggestion = "Use definition, explanation and example."

    return good,missing,suggestion


# -------------------------
# SAVE RESULTS
# -------------------------

def save_results(role,answers,scores,avg):

    df = pd.DataFrame({

    "Role":[role],
    "Answers":[answers],
    "Scores":[scores],
    "Average":[avg]

    })

    df.to_csv("interview_results.csv",mode="a",index=False)


# -------------------------
# SESSION STATE
# -------------------------

if "start" not in st.session_state:
    st.session_state.start=False

if "i" not in st.session_state:
    st.session_state.i=0

if "answers" not in st.session_state:
    st.session_state.answers=[]

if "scores" not in st.session_state:
    st.session_state.scores=[]

if "questions" not in st.session_state:
    st.session_state.questions=[]


# -------------------------
# START INTERVIEW
# -------------------------

if st.button("Start Interview"):

    st.session_state.start=True

    st.session_state.i=0

    st.session_state.answers=[]

    st.session_state.scores=[]

    st.session_state.questions=generate_questions(role)


# -------------------------
# INTERVIEW FLOW
# -------------------------

if st.session_state.start:

    i = st.session_state.i

    questions = st.session_state.questions

    if i < len(questions):

        question = questions[i]

        st.subheader(f"Question {i+1}")

        st.write(question)

        speak(question)

        st.progress(i/len(questions))

        audio = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key=f"rec{i}"
        )

        if audio:

            st.audio(audio["bytes"])

            answer = speech_to_text(audio["bytes"])

            st.write("Recognized Answer:",answer)

            score = evaluate_answer(answer,question)

            good,missing,suggestion = generate_feedback(score)

            st.write("Score:",score)

            st.write("Good:",good)

            st.write("Missing:",missing)

            st.write("Suggestion:",suggestion)

            st.session_state.answers.append(answer)

            st.session_state.scores.append(score)

            st.session_state.i += 1


    else:

        st.success("Interview Completed")

        total=sum(st.session_state.scores)

        avg=total/len(st.session_state.scores)

        st.subheader("Final Interview Report")

        st.write("Total Score:",total)

        st.write("Average Score:",avg)

        if avg>=8:

            feedback="Excellent performance"

        elif avg>=6:

            feedback="Good but improve explanations"

        else:

            feedback="Needs more practice"

        st.write("Final Feedback:",feedback)

        save_results(role,st.session_state.answers,st.session_state.scores,avg)

        st.success("Results saved to CSV")