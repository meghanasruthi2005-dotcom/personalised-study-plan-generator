import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import os
import smtplib
from email.mime.text import MIMEText

# -------- UI STYLE --------
st.markdown("""
<style>
.stApp{
background: linear-gradient(135deg,#dbeafe,#f0f9ff);
color:black;
}

label{
color:#1e3a8a !important;
font-weight:bold;
font-size:16px;
}

input,textarea{
background-color:#ffffff !important;
color:black !important;
border-radius:6px;
}
</style>
""",unsafe_allow_html=True)

st.title("📚 RCE Personalised Study Plan Generator")

name = st.text_input("Student Name")
subject = st.text_input("Subject")
email = st.text_input("Enter Gmail for Reminder")

deadline_time = st.time_input("Daily Study Deadline Time")

exam_marks = st.number_input("Exam Total Marks",min_value=1)

exam_date = st.date_input("Exam Date")
concepts_input = st.text_area("Enter Concepts (comma separated)")

file_name="study_plan_data.csv"

concept_list=[]

if concepts_input:
    concept_list=[c.strip() for c in concepts_input.split(",") if c.strip()!=""]

    st.subheader("Select Difficulty for Each Concept")

    difficulty_map={}

    for c in concept_list:
        difficulty_map[c]=st.selectbox(
            f"{c} difficulty",
            ["Easy","Medium","Hard"],
            key=c
        )

generate = st.button("Generate Timetable")

if generate:

    today=date.today()
    total_days=(exam_date-today).days

    if not concept_list:
        st.error("Please enter concepts first.")

    elif total_days <= 0:
        st.error("Exam date must be after today.")

    else:

        weighted_concepts=[]

        for c in concept_list:

            diff=difficulty_map[c]

            if diff=="Hard":
                weighted_concepts += [c]*3
            elif diff=="Medium":
                weighted_concepts += [c]*2
            else:
                weighted_concepts += [c]

        schedule=[]
        hours_list=[]

        while len(schedule) < total_days:
            for topic in weighted_concepts:
                if len(schedule) < total_days:
                    schedule.append(topic)

                    diff=difficulty_map[topic]

                    if diff=="Hard":
                        hrs=3.5
                    elif diff=="Medium":
                        hrs=2.5
                    else:
                        hrs=1.5

                    hours_list.append(hrs)

        dates=[today+timedelta(days=i) for i in range(total_days)]

        df=pd.DataFrame({
            "Date":dates,
            "Subject":[subject]*total_days,
            "Concepts":schedule,
            "Study Hours":hours_list,
            "Completed":[False]*total_days
        })

        df.to_csv(file_name,index=False)

        st.session_state["generated"]=True

        st.success("Timetable Generated Successfully!")

# -------- LOAD TIMETABLE --------

if "generated" in st.session_state and os.path.exists(file_name):

    df=pd.read_csv(file_name)

    st.subheader("📅 Your Study Timetable")

    completed_count=0

    for i in range(len(df)):

        col1,col2,col3,col4,col5=st.columns([2,2,3,2,1])

        with col1:
            st.write(df["Date"].iloc[i])

        with col2:
            st.write(df["Subject"].iloc[i])

        with col3:
            st.write(df["Concepts"].iloc[i])

        with col4:
            st.write(str(df["Study Hours"].iloc[i])+" hrs")

        with col5:

            allow_tick=True

            if i>0 and df["Completed"].iloc[i-1]==False:
                allow_tick=False

            done=st.checkbox(
                "",
                value=False if df["Completed"].iloc[i]==False else True,
                key=f"task{i}",
                disabled=not allow_tick
            )

            df.at[i,"Completed"]=done

            if done:
                completed_count+=1

    df.to_csv(file_name,index=False)

    progress=completed_count/len(df)

    st.subheader("📊 Study Progress")
    st.progress(progress)

    if completed_count==len(df):

        st.success(f"""
🎉 Excellent work {name}!  

📚 You successfully completed your entire study plan.  

💪 You prepared very well and stayed disciplined throughout your study journey.  

🔥 You are ready now — go write your exam confidently and score great marks!  

✨ All the best for your exam!
""")

    today_str=str(date.today())

    pending=df[(df["Date"]==today_str) & (df["Completed"]==False)]

    current_time=datetime.now().time()

    if len(pending)>0 and current_time > deadline_time:

        st.error("⚠ Reminder: Deadline crossed and today's task not completed!")

        if email!="":

            try:

                sender="meghanasruthi2005@gmail.com"
                password="syxaqolwflfwpnbg"

                msg=MIMEText(f"""
Hello {name},

You missed today's study deadline.

Topic: {pending.iloc[0]['Concepts']}

Deadline time: {deadline_time}

Please complete it as soon as possible and stay on track for your exam.

Good luck 📚
""")

                msg["Subject"]="Study Deadline Reminder"
                msg["From"]=sender
                msg["To"]=email

                server=smtplib.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(sender,password)
                server.sendmail(sender,email,msg.as_string())
                server.quit()

            except:
                st.warning("Email reminder setup required.")