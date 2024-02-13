import os
import streamlit as st

#import RubricGuide
from ai_uni.Faculty.LabReport.rubric_guide import LabGuider

rubric = "./ai_uni/Faculty/LabReport/rubric.txt"
procedure = "./ai_uni/Faculty/LabReport/procedure.txt"

# Streamlit app
st.title("Lab Report Assistant")

#just txt for now - pdf maybe later
report = st.file_uploader(
    "Upload your report as a txt file", type=["txt"],)
# write file to disk
if report:
    with open(report.name, "wb") as f:
        f.write(report.getbuffer())

    st.write("Files successfully uploaded!")
    uploaded_file = os.path.join(os.getcwd(), report.name)
else:
    uploaded_file=""
    print ("No file uploaded")


guide = LabGuider(file=uploaded_file, rubric=rubric, procedure=procedure)

def generate_response(prompt):
    result = guide.run(prompt)
    return result


# make new container to store scratch
scratch = st.empty()
scratch.write(
    """Hi! I am the Lab Report Assistant for the Lab: Determination of the Molar Mass of an Unknown Acid through Acid-Base Titration. Please upload your lab report and I will guide you through the rubric and help you improve your report. Let me know when you're ready!"""
)


if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        response = guide.run()
        st.write(response)