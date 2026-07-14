import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Load environment configuration
load_dotenv()

# Set up Streamlit Page Page Title & Premium design theme
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="centered"
)

# Custom premium CSS for visuals
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        color: white;
    }
    .explanation-box {
        background-color: #262930;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize connection to local Ollama LLM
@st.cache_resource
def get_llm():
    return LLM(
        model=os.getenv("OPENAI_MODEL_NAME"),
        base_url=os.getenv("OPENAI_API_BASE")
    )

local_llm = get_llm()

# Initialize Agents
@st.cache_resource
def get_agents():
    topic_agent = Agent(
        role="Topic Explanation Expert",
        goal="Provide clear, concise, and engaging explanations of educational topics.",
        backstory="You are an expert educator who specializes in breaking down complex concepts "
                  "into simple, easy-to-understand explanations for students.",
        llm=local_llm,
        allow_delegation=False,
        max_iter=3
    )

    quiz_agent = Agent(
        role="Educational Quiz Designer",
        goal="Design effective multiple-choice questions based on provided text.",
        backstory="You are a professional assessment creator. You analyze educational materials "
                  "and construct clear, balanced multiple-choice questions to test comprehension.",
        llm=local_llm,
        allow_delegation=False,
        max_iter=3
    )

    feedback_agent = Agent(
        role="Tutor Evaluator",
        goal="Evaluate the user's quiz answers against the topic material and provide constructive, friendly feedback.",
        backstory="You are an encouraging and supportive private tutor. You review a student's answers, "
                  "explain why answers are correct or incorrect based on the educational material, and help them improve.",
        llm=local_llm,
        allow_delegation=False,
        max_iter=3
    )
    
    return topic_agent, quiz_agent, feedback_agent

topic_agent, quiz_agent, feedback_agent = get_agents()

# Initialize session state variables to store outputs between steps
if "explanation" not in st.session_state:
    st.session_state.explanation = ""
if "quiz" not in st.session_state:
    st.session_state.quiz = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

st.title("🎓 AI Study Buddy")
st.write("Your local sequential multi-agent learning companion powered by local Ollama.")

# Form to enter the study topic
topic_input = st.text_input("What topic would you like to study today?", placeholder="e.g., Photosynthesis, Gravity, AI...")

if st.button("Start Lesson"):
    if topic_input:
        with st.spinner("Topic Agent & Quiz Agent are preparing your lesson..."):
            # Setup Tasks
            explain_task = Task(
                description=f"Generate a clear and concise explanation of the topic: '{topic_input}'. "
                            "Break down any complex terms and make it engaging for a beginner student.",
                expected_output="A structured explanation of the topic with key definitions and a simple summary.",
                agent=topic_agent
            )

            quiz_task = Task(
                description="Analyze the generated explanation of the topic. Create exactly 3 multiple-choice questions (MCQs) "
                            "based on the material. Each question should have options (A, B, C, D). "
                            "CRITICAL: Do NOT show, mention, or print the correct answers anywhere in the generated quiz questions. "
                            "Keep them completely hidden so the student can answer them.",
                expected_output="A list of 3 multiple-choice questions with choices, without showing the correct answers.",
                agent=quiz_agent
            )

            # Sequential execution of explanation & quiz creation
            crew_phase1 = Crew(
                agents=[topic_agent, quiz_agent],
                tasks=[explain_task, quiz_task],
                process=Process.sequential
            )
            
            phase1_output = crew_phase1.kickoff()
            
            # Store output in session state
            st.session_state.explanation = explain_task.output.raw if explain_task.output else ""
            st.session_state.quiz = quiz_task.output.raw if quiz_task.output else str(phase1_output)
            st.session_state.feedback = "" # reset feedback for new topic
    else:
        st.warning("Please enter a topic first!")

# Display Phase 1 results if they exist
if st.session_state.explanation:
    st.header("📖 1. Study material")
    st.markdown(f'<div class="explanation-box">{st.session_state.explanation}</div>', unsafe_allow_html=True)
    
    st.header("📝 2. Practice Quiz")
    st.write("Review the generated questions below and write down your answers:")
    st.text(st.session_state.quiz)
    
    st.subheader("Submit your Answers")
    ans1 = st.text_input("Answer for Question 1 (A/B/C/D):", key="ans1_val")
    ans2 = st.text_input("Answer for Question 2 (A/B/C/D):", key="ans2_val")
    ans3 = st.text_input("Answer for Question 3 (A/B/C/D):", key="ans3_val")
    
    if st.button("Submit Answers"):
        user_answers = f"Q1: {ans1}\nQ2: {ans2}\nQ3: {ans3}"
        with st.spinner("Feedback Agent is evaluating your answers..."):
            # Feedback Task setup
            feedback_task = Task(
                description=(
                    f"Review the original explanation:\n{st.session_state.explanation}\n\n"
                    f"Review the quiz questions:\n{st.session_state.quiz}\n\n"
                    f"Grade the student's answers:\n{user_answers}\n\n"
                    "Assess whether the answers are correct or incorrect. Provide friendly, clear explanation "
                    "for each question, explaining why the answer is correct or incorrect based on the material. "
                    "At the very beginning of your response, write a clear final score (e.g. 'Score: 2/3' or 'Score: 3/3'). "
                    "At the end of your message, sign off simply with 'Best regards,\nYour AI Study Buddy'. "
                    "Do NOT use brackets or placeholders like '[Your Name]' or '[Your Title]'."
                ),
                expected_output="A friendly report starting with a final numeric score (e.g. Score: 2/3), grading each question, and signing off cleanly.",
                agent=feedback_agent
            )

            crew_phase2 = Crew(
                agents=[feedback_agent],
                tasks=[feedback_task],
                process=Process.sequential
            )
            
            final_feedback = crew_phase2.kickoff()
            st.session_state.feedback = final_feedback.raw if hasattr(final_feedback, 'raw') else str(final_feedback)

# Display Tutor Feedback if it exists
if st.session_state.feedback:
    st.header("🧑‍🏫 3. Tutor Feedback")
    st.markdown(st.session_state.feedback)
