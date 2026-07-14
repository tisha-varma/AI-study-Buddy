import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Load local environment configuration (.env)
load_dotenv()

# Initialize our connection to the local Ollama LLM
local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# 1. Topic Agent
topic_agent = Agent(
    role="Topic Explanation Expert",
    goal="Provide clear, concise, and engaging explanations of educational topics.",
    backstory="You are an expert educator who specializes in breaking down complex concepts "
              "into simple, easy-to-understand explanations for students.",
    llm=local_llm,
    allow_delegation=False,
    max_iter=3,
    verbose=True
)

# 2. Quiz Agent
quiz_agent = Agent(
    role="Educational Quiz Designer",
    goal="Design effective multiple-choice questions based on provided text.",
    backstory="You are a professional assessment creator. You analyze educational materials "
              "and construct clear, balanced multiple-choice questions to test comprehension.",
    llm=local_llm,
    allow_delegation=False,
    max_iter=3,
    verbose=True
)

# 3. Feedback Agent
feedback_agent = Agent(
    role="Tutor Evaluator",
    goal="Evaluate the user's quiz answers against the topic material and provide constructive, friendly feedback.",
    backstory="You are an encouraging and supportive private tutor. You review a student's answers, "
              "explain why answers are correct or incorrect based on the educational material, and help them improve.",
    llm=local_llm,
    allow_delegation=False,
    max_iter=3,
    verbose=True
)

if __name__ == "__main__":
    print("=== Welcome to AI Study Buddy ===")
    topic = input("Enter a topic you want to study today: ")
    print(f"\n=== Starting AI Study Buddy for Topic: {topic} ===")
    
    # --- PHASE 1: Topic Explanation & Quiz Creation ---
    
    explain_task = Task(
        description=f"Generate a clear and concise explanation of the topic: '{topic}'. "
                    "Break down any complex terms and make it engaging for a beginner student.",
        expected_output="A structured explanation of the topic with key definitions and a simple summary.",
        agent=topic_agent
    )

    quiz_task = Task(
        description="Analyze the generated explanation of the topic. Create exactly 3 multiple-choice questions (MCQs) "
                    "based on the material. Each question should have options (A, B, C, D) and specify the correct answer.",
        expected_output="A list of 3 multiple-choice questions with choices and the correct answers marked.",
        agent=quiz_agent
    )

    # Crew 1: Run the Topic Explanation and Quiz generation
    crew_phase1 = Crew(
        agents=[topic_agent, quiz_agent],
        tasks=[explain_task, quiz_task],
        process=Process.sequential,
        verbose=True
    )

    # Kickoff Phase 1
    phase1_output = crew_phase1.kickoff()
    
    # Extract outputs
    explanation_text = explain_task.output.raw if explain_task.output else ""
    quiz_text = quiz_task.output.raw if quiz_task.output else str(phase1_output)

    print("\n==========================================")
    print("=== STEP 1: READ THE EXPLANATION ===")
    print("==========================================\n")
    print(explanation_text)

    print("\n==========================================")
    print("=== STEP 2: TAKE THE QUIZ ===")
    print("==========================================\n")
    print(quiz_text)

    # --- PHASE 2: Human Answer Gathering ---
    print("\n--- Please enter your answers below ---")
    ans1 = input("Your answer for Question 1 (e.g., A): ")
    ans2 = input("Your answer for Question 2 (e.g., B): ")
    ans3 = input("Your answer for Question 3 (e.g., C): ")
    user_answers = f"Q1: {ans1}\nQ2: {ans2}\nQ3: {ans3}"

    # --- PHASE 3: Feedback Agent ---
    feedback_task = Task(
        description=(
            f"Review the original explanation:\n{explanation_text}\n\n"
            f"Review the quiz questions:\n{quiz_text}\n\n"
            f"Grade the student's answers:\n{user_answers}\n\n"
            "Assess whether the answers are correct or incorrect. Provide friendly, clear explanation "
            "for each question, explaining why the answer is correct or incorrect based on the material. "
            "At the very beginning of your response, write a clear final score (e.g. 'Score: 2/3' or 'Score: 3/3'). "
            "At the end of your message, sign off simply with 'Best regards,\nYour AI Study Buddy'. "
            "Do NOT use brackets or placeholders like '[Your Name]' or '[Your Title]'."
        ),
        expected_output="A friendly report starting with a final numeric score (e.g. Score: 2/3), grading each question and explaining the correct answers, signed off cleanly.",
        agent=feedback_agent
    )

    crew_phase2 = Crew(
        agents=[feedback_agent],
        tasks=[feedback_task],
        process=Process.sequential,
        verbose=True
    )

    print("\nEvaluating your answers...")
    final_feedback = crew_phase2.kickoff()

    print("\n==========================================")
    print("=== STEP 3: TUTOR FEEDBACK ===")
    print("==========================================\n")
    print(final_feedback)
