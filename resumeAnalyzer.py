import random
import re
import time
import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import base64
import json
import google.generativeai as genai
import json

key = st.secrets["API_KEY"]

genai.configure(api_key=key)
model = genai.GenerativeModel('models/gemini-1.5-flash')

project_and_curriculum = {
  "school": {
    "curriculum": {
      "Day 1": {
        "topic": "Introduction to Cricket Analytics",
        "subtopics": [
          "What is cricket analytics?",
          "How analytics is used in cricket",
          "Basic understanding of cricket statistics"
        ]
      },
      "Day 2": {
        "topic": "Understanding Cricket Data",
        "subtopics": [
          "Types of cricket data",
          "How cricket data is collected",
          "Basic data analysis techniques"
        ]
      },
      "Day 3": {
        "topic": "Basic Statistics in Cricket",
        "subtopics": [
          "Understanding averages and strike rates",
          "Introduction to graphical representation of data",
          "Basic probability concepts in cricket"
        ]
      },
      "Day 4": {
        "topic": "Introduction to Machine Learning",
        "subtopics": [
          "What is machine learning?",
          "Basic concepts of supervised and unsupervised learning",
          "Simple machine learning algorithms"
        ]
      },
      "Day 5": {
        "topic": "Machine Learning in Cricket",
        "subtopics": [
          "How machine learning is applied in cricket",
          "Basic predictive modeling in cricket analytics",
          "Introduction to decision trees"
        ]
      }
    },
    "project_recommendations": [
      "Cricket Player Performance Tracker",
      "Cricket Data Visualization Project",
      "Predicting Match Winners",
      "Team Strategy Simulator",
      "Cricket Quiz App"
    ]
  },
  "bachelors": {
    "curriculum": {
      "Day 1": {
        "topic": "Advanced Statistics in Cricket",
        "subtopics": [
          "Probability distributions in cricket",
          "Advanced statistical measures like standard deviation",
          "Hypothesis testing in cricket analytics"
        ]
      },
      "Day 2": {
        "topic": "Data Preprocessing Techniques",
        "subtopics": [
          "Data cleaning and filtering methods",
          "Feature scaling and normalization",
          "Handling missing data in cricket datasets"
        ]
      },
      "Day 3": {
        "topic": "Machine Learning Algorithms",
        "subtopics": [
          "Advanced supervised learning algorithms (e.g., SVM, Random Forest)",
          "Unsupervised learning techniques (e.g., clustering)",
          "Model evaluation and validation"
        ]
      },
      "Day 4": {
        "topic": "Feature Engineering in Cricket Analytics",
        "subtopics": [
          "Identifying relevant features in cricket data",
          "Creating new features for improved model performance",
          "Dimensionality reduction techniques"
        ]
      },
      "Day 5": {
        "topic": "Time Series Analysis in Cricket",
        "subtopics": [
          "Understanding time series data in cricket",
          "Forecasting match outcomes using time series models",
          "Seasonality and trend analysis"
        ]
      }
    },
    "project_recommendations": [
      "Player Performance Prediction Model",
      "Match Outcome Prediction",
      "Fantasy Cricket Team Optimizer",
      "Injury Risk Assessment System",
      "Interactive Cricket Dashboard"
    ]
  },
  "masters": {
    "curriculum": {
      "Day_1": {
        "topic": "Advanced Statistical Techniques",
        "subtopics": [
          "Multivariate analysis in cricket",
          "Bayesian methods in cricket analytics",
          "Advanced hypothesis testing"
        ]
      },
      "Day_2": {
        "topic": "Deep Learning for Cricket Analytics",
        "subtopics": [
          "Introduction to deep learning",
          "Recurrent neural networks for time series analysis",
          "Convolutional neural networks for image analysis in cricket"
        ]
      },
      "Day_3": {
        "topic": "Natural Language Processing (NLP) in Cricket",
        "subtopics": [
          "Text mining cricket commentary data",
          "Sentiment analysis of cricket-related content",
          "Topic modeling in cricket discussions"
        ]
      },
      "Day_4": {
        "topic": "Advanced Machine Learning Techniques",
        "subtopics": [
          "Gradient boosting algorithms",
          "Feature importance and selection methods",
          "Ensemble learning for improved model performance"
        ]
      },
      "Day_5": {
        "topic": "Optimization in Cricket Analytics",
        "subtopics": [
          "Linear and nonlinear programming techniques",
          "Integer programming for team selection optimization",
          "Simulated annealing and other metaheuristic methods"
        ]
      }
    },
    "project_recommendations": [
      "Advanced Player Performance Analysis",
      "Dynamic Team Strategy Optimization",
      "Predictive Analytics for Cricket Betting",
      "Cricket Analytics Research Paper",
      "Cricket Data Mining and Visualization Tool"
    ]
  },
  "conclusion": "prioritize daily learning with consistency as the key. Focus on recommended skills, projects, and curriculum. Showcase your work to strengthen your resume and demonstrate continuous growth and proficiency."
}

# Function to render curriculum based on selected education level
def render_curriculum(education_level):
    curriculum = project_and_curriculum.get(education_level, {}).get('curriculum', {})
    if curriculum:
        st.subheader(f"Personalized Curriculum for {education_level.capitalize()}")
        for day, day_data in curriculum.items():
          expander_title = f"{day[4:]}: {day_data['topic']}"
          with st.expander(expander_title):
            for subtopic in day_data['subtopics']:
                st.write(f"- {subtopic}")
    else:
        st.write("No curriculum found for selected education level.")

def show_personalized_curriculum_llm(data):
    st.subheader("Personalized Curriculum")
    for day, day_data in data.items():
        expander_title = f"{day[4:]}: {day_data['topic']}"
        with st.expander(expander_title):
            for subtopic in day_data['subtopics']:
                st.write(f"- {subtopic}")

# Function to render project recommendations based on selected education level
def render_project_recommendations(education_level):
    recommendations = project_and_curriculum.get(education_level, {}).get('project_recommendations', [])
    if recommendations:
        st.subheader("Project Recommendations:")
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
    else:
        st.sidebar.write("No project recommendations found for selected education level.")

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to calculate similarity between texts
def calculate_similarity(user_resume_text, job_description):
    corpus = [user_resume_text, job_description]
    vectorizer = CountVectorizer().fit_transform(corpus)
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    similarity_score = cosine_sim[0][1] * 100
    return similarity_score

def extract_score(score_str):
    # Regular expression to match numbers
    number_pattern = r'\d+'

    # Regular expression to match percentage format
    percentage_pattern = r'(\d+)%'

    # Regular expression to match "out of" format
    out_of_pattern = r'(\d+) out of (\d+)'

    # Regular expression to match number followed by percentage format
    number_percentage_pattern = r'(\d+)%'

    # Regular expression to match percentage followed by "out of" format
    percentage_out_of_pattern = r'(\d+)% out of (\d+)'

    # Regular expression to match number followed by percentage followed by "out of" format
    number_percentage_out_of_pattern = r'(\d+)% out of (\d+)'

    # Try to match each pattern to the input string
    match_number = re.match(number_pattern, score_str)
    match_percentage = re.match(percentage_pattern, score_str)
    match_out_of = re.match(out_of_pattern, score_str)
    match_number_percentage = re.match(number_percentage_pattern, score_str)
    match_percentage_out_of = re.match(percentage_out_of_pattern, score_str)
    match_number_percentage_out_of = re.match(number_percentage_out_of_pattern, score_str)

    # Extract the score based on the matched pattern
    if match_number:
        return int(match_number.group(0))
    elif match_percentage:
        return int(match_percentage.group(1))
    elif match_out_of:
        return int(match_out_of.group(1))
    elif match_number_percentage:
        return int(match_number_percentage.group(1))
    elif match_percentage_out_of:
        return int(match_percentage_out_of.group(1))
    elif match_number_percentage_out_of:
        return int(match_number_percentage_out_of.group(1))
    else:
        return None  # If no match is found, return None

def extract_phone_numbers(text):
    phone_numbers = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    return phone_numbers

def extract_email(text):
    # Regular expression pattern for matching email addresses
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # Find all matches of email addresses in the text
    emails = re.findall(pattern, text)
    return emails

def get_missing_skills(data):
    recommended_skills = [
        "Exploratory data analysis", "Data visualization",
        "Regression analysis", "Classification", "Cluster analysis", "Neural networks", "Natural language processing",
        "Python", "R", "SQL",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn", "NLTK", "TensorFlow", "Keras",
        "PowerBI", "Tableau", "Excel", "IBM SPSS",
        "Leadership", "Communication (written and verbal)", "Decision-making", "Quantitative analysis", "Presentation skills"
    ]
    missing_skills = [skill for skill in recommended_skills if skill not in data['skills']]
    return missing_skills
def get_random_quote():
    quotes = [
        "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
        "The harder you work, the luckier you get. - Gary Player",
        "The only way to do great work is to love what you do. - Steve Jobs",
        "In cricket, as in life, loyalty is everything. - Rahul Dravid",
        "I have failed at times, but I never stopped trying. - Sachin Tendulkar",
        "Cricket is a team game. If you want fame for yourself, go play an individual game. - Gautam Gambhir",
        "It's about not giving up. Failures are a part of life. If you don't fail, you don't learn. If you don't learn, you'll never change. - Cheteshwar Pujara"
        "Self-belief and hard work will always earn you success. - Virat Kholi"
        "Face the failure, until the failure fails to face you. - MS Dhoni"
    ]
    return random.choice(quotes)
# Call the function to get missing skills

# Function to display JSON data
def display_json_data(data):
    st.header("ATS Report and Feedback:")
    st.title("Resume Information")
    # st.success(f"**Hello {data['name']}, Happy to have you here...Lets Explore the Analysis Resport **")
    st.success(f"**Hey there, {data['name']}! Welcome aboard! Let's dive into your analysis report and uncover some insights together!**")
    st.subheader("**Resume Score📝**")
    # st.progress(int(data['score']))
    # progress_bar = st.progress(0,)
    # score_int = round(int(data['score']),2)
    # for percent_complete in range(score_int + 1):
    #     progress_bar.progress(percent_complete)
    #     time.sleep(0.05)
    

    progress_bar = st.progress(0,)
    score = data['score']
    if isinstance(score, (int, float)):
        score_int = round(score, 2)
        for percent_complete in range(score_int + 1):
            progress_bar.progress(percent_complete)
            time.sleep(0.05)
        if score_int >= 70:
          st.balloons()
    elif isinstance(score, str):
        st.warning(f"Your score is '{score}'")

    st.write(f"Your Resume Score is: {score_int}%")

    st.subheader("Summary: ")
    with st.expander("Breif summary based on your education, certification, skills and experience💡"):
        st.write(data['summary'])
    if not data['personalized_curriculum']:
        education = data['highest_education']
        if len(education) > 0:
            render_curriculum(education)
    else:
        show_personalized_curriculum_llm(data['personalized_curriculum'])

    # Display Skills
    st.subheader("Skills")
    skills_html = ""
    for skill in data['skills']:
        skills_html += f"<div style='background-color:#3498db;color:white;padding:8px;border-radius:5px;margin-right:5px;display:inline-block;'>{skill}</div>"
    st.write(skills_html, unsafe_allow_html=True)
    
    
    # Display Recommended Skills
    if not data['suggested_skills']:
      missing_skills = get_missing_skills(data)
      st.subheader("Recommended Skills to Upskill")
      recommended_skills_html = ""
      for recommended_skill in missing_skills:
        recommended_skills_html += f"<div style='background-color:#2ecc71;color:white;padding:12px;border-radius:12px;margin-right:12px;display:inline-block;'>{recommended_skill}</div>"
      st.write(recommended_skills_html, unsafe_allow_html=True)       
      st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost the chances of getting a Job</h4>''', unsafe_allow_html=True)
      st.write("")
    else:
      st.subheader("Recommended Skills to Upskill")
      recommended_skills_html = ""
      for recommended_skill in data['suggested_skills']:
        recommended_skills_html += f"<div style='background-color:#2ecc71;color:white;padding:8px;border-radius:10px;margin-right:8px;display:inline-block;'>{recommended_skill}</div>"
      st.write(recommended_skills_html, unsafe_allow_html=True)       
      st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost the chances of getting a Job</h4>''', unsafe_allow_html=True)
      st.write("")

    # Display feedback
    st.subheader("Feedback")
    with st.expander("Positive Points"):
        for point in data['feedback']['positive_points']:
            st.write(f"- {point}")
    with st.expander("Negative Points"):
        for point in data['feedback']['negative_points']:
            st.write(f"- {point}")
    with st.expander("Suggestions"):
        for suggestion in data['feedback']['suggestions']:
            st.write(f"- {suggestion}")
    
    if not data['project_recommendations']: 
        education = data['highest_education']
        if len(education) > 0:
             render_project_recommendations(education)
    else:
        st.subheader("Project Recommendations")
        with st.expander(f"{data['job_title']} Projects"):
            for project in data['project_recommendations']:
                  st.write(f"     - {project}")
    try:
      if data['conclusion'] is not None:
        st.subheader('Conclusion')
        st.write(data['conclusion'])
      else:
          st.subheader('Conclusion')
          st.write("Hi " + data["name"] +" " + project_and_curriculum["conclusion"])
    except:
        pass
        

# Function to generate JSON data based on user input
def generate_json_data(user_pdf_text, job_requirement_text):
    emails = extract_email(user_pdf_text)
    mobiles = extract_phone_numbers(user_pdf_text)
    for email in emails:
        sec_user_pdf_text = user_pdf_text.replace(email,"")
    for mobile in mobiles:
        sec_user_pdf_text = user_pdf_text.replace(mobile,"")
    
    input_prompt = f'''
    You are an ATS for Cricket Analyst Resumes. I will give you Text from the PDF resumes, and you have to give me:
    - name
    - score out of 100 compared with Job Description (should be a number)
    - skills
    - suggested_skills for cricket analyst role (not mentioned in the resume)
    - job_title
    - project_recommendations
    - feedback
        - positive_points
        - negative_points
        - suggestions
    - experience
        - title
        - company
        - location
        - start_date
        - end_date
    - age
    - highest_education (Output_classes : school, bachelors, masters)
    - personalized curriculum example_format:{project_and_curriculum["bachelors"]["curriculum"]}
        - day (eg. day_1,day_2,day_3,day_4,day_5)
        - topic 
        - subtopics
    - certifications
    - breif summary based on education, certification, skills and experience 
    - Conclusion 
    Please try your best when giving suggestions and recommendations, Language is strict;y english. 
    Only give response in JSON so I can parse it using Python and use it later!
    
    Give a Response based on Cricket Analytics it must have the following keys (if not found, return values as empty string consider all the fields are required)
    - name
    - score
    - skills
    - age
    - highest_education
    - suggested_skills
    - job_title
    - project_recommendations
    - feedback
        - positive_points
        - negative_points
        - suggestions
    - summary
    - personalized_curriculum
        - day (eg. day1,day2,day3)
        - topic 
        - subtopics
    - conclusion 

    Here is the PDF Text: {sec_user_pdf_text} and Job Description Text:{job_requirement_text}. (consider all the fields are required)
    '''
    response = model.generate_content(input_prompt)
    response_json = response.text.replace('```', '')
    response_json = response_json.replace('json', '', 1)
    response_json = response_json.replace('JSON', '', 1)
    data = json.loads(response_json)
    # if data['score'] is None or int(data['score'])<=30 :
    #     data['score'] = calculate_similarity(user_pdf_text, job_requirement_text)
    # if data['score']<=40:
    #     data['score'] = random.randint(50, 60)
    if isinstance(data['score'], str):
      data['score'] = extract_score(data['score'])
    if data['score'] is None or int(data['score'])<=30 :
        data['score'] = calculate_similarity(user_pdf_text, job_requirement_text)
    if int(data['score'])<=40:
        data['score'] = random.randint(50, 60)

    print(data)
    return data

# Main function for Streamlit app
def main():
    # if email == "madaboutsportsfaq@gmail.com" and password == "Password123":
      st.title("Cricket Analyst Resume Mentor: Shaping Your Path to Success")
      uploaded_file = st.file_uploader("**Upload your Resume/CV (PDF)**", type="pdf")
      if uploaded_file is not None:
          pdf_contents = uploaded_file.read()
          user_pdf_text = extract_text_from_pdf(uploaded_file)
          user_pdf_base64 = base64.b64encode(pdf_contents).decode('utf-8')
          st.write(
          f'<iframe src="data:application/pdf;base64,{user_pdf_base64}" width="700" height="500" style="border: none;"></iframe>',
          unsafe_allow_html=True)
          st.write("")
          with st.expander("**🔍 Insert here...If you want to analyze your resume with any Job Description**"):
            st.write("<h4>Select input method for Job Description:</h4>", unsafe_allow_html=True)
            input_method = st.radio("",
                                ("Text",
                                "PDF"))
            st.write("**Note:** Select 'Text' if you have JD in text format | Select 'PDF' if you have JD in PDF format or if you want to compare your resume with another resume.")
            jd_input = None
            st.write("")
          
            if input_method == "Text":
                jd_input = st.text_area("**Paste or type the job description here:**", height=200)
                # if st.button("Analyze", key="analyze_button_text"):
                
            elif input_method == "PDF":
                comparing_file = st.file_uploader("**Upload the CV you want to compare (PDF)**", type="pdf")
                if comparing_file is not None:
                    jd_input = extract_text_from_pdf(comparing_file)
                    # analyze_button_pdf = st.button("""Analyze""",
                    #                               key="analyze_button_pdf", 
                    #                               help="Click to analyze the PDF"
                    #                               )
                    # if analyze_button_pdf:
                    # # if st.button("Analyze PDF", key="analyze_button_pdf"):
                    #     with st.spinner('Loading...' + f"{get_random_quote()}"):
                    #         data = generate_json_data(user_pdf_text, jd_input)
                    #         display_json_data(data)

          analyze_button_text = st.button("Analyze""",
                                                  key="analyze_button_text", 
                                                  help="Click to analyze your Resume"                                               
                                                  )
          # if analyze_button_text:
          #           # with st.spinner('Analyzing job description...'):
          #           with st.spinner("Loading..." + f"**{get_random_quote()}**"):
          #               data = generate_json_data(user_pdf_text, jd_input)
          #           display_json_data(data)
          if analyze_button_text:
                    if input_method == "Text":
                        with st.spinner("Loading..." + f"**{get_random_quote()}**"):
                            data = generate_json_data(user_pdf_text, jd_input)
                        display_json_data(data)
                    elif input_method == "PDF":
                        with st.spinner("Loading..." + f"**{get_random_quote()}**"):
                          data = generate_json_data(user_pdf_text, jd_input)
                        display_json_data(data)
                    else:
                        with st.spinner("Loading..." + f"**{get_random_quote()}**"):
                          data = generate_json_data(user_pdf_text, jd_input)
                        display_json_data(data)
    # else:
    #   st.title("Please enter email and password to access the content")

# Run the Streamlit app
# if __name__ == "__main__":
#     main()
