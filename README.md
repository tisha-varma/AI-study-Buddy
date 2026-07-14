# 🎓 AI Study Buddy

AI Study Buddy is a local, sequential, multi-agent learning companion. It helps you study any custom topic by generating educational material, creating practice quizzes, and providing interactive tutoring feedback. 

The system runs entirely locally on your machine using **Ollama**, **Mistral**, and **CrewAI**.

---

## 🧠 System Architecture & Workflow

The system utilizes exactly **3 specialized agents** executing in a strict sequential chain:

```
[ User Topic Input ]
         │
         ▼
 ┌───────────────┐
 │  Topic Agent  │ ──► Generates clear explanation
 └───────────────┘
         │
         ▼
 ┌───────────────┐
 │  Quiz Agent   │ ──► Analyzes explanation & creates practice questions
 └───────────────┘
         │
         ▼
[ User Answers Input ]
         │
         ▼
 ┌───────────────┐
 │Feedback Agent │ ──► Grades answers & provides tutoring feedback
 └───────────────┘
         │
         ▼
[ Tutor Evaluation & Score ]
```



### Flow Details:
1. **Topic Agent**: Simulates an expert teacher, generating clean and structured explanations of complex concepts for beginners.
2. **Quiz Agent**: Receives the Topic Agent's explanation and constructs 3 multiple-choice questions (MCQs) with options, keeping correct answers hidden.
3. **Feedback Agent**: Receives the original material, the questions, and the user's input answers. It grades the answers, provides explanations for each correct/incorrect option, and calculates a final score (e.g., `2/3`).

---


https://github.com/user-attachments/assets/7dacf856-787b-46eb-9afe-eefcfac16614


## 🛠️ Tech Stack & Setup

*   **Language**: Python 3.12+
*   **Orchestration**: CrewAI
*   **Local LLM**: Ollama (Mistral model)
*   **UI Framework**: Streamlit

### Prerequisites

1.  Download and install [Ollama](https://ollama.com/).
2.  Pull the Mistral model in your terminal:
    ```bash
    ollama pull mistral
    ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tisha-varma/AI-study-Buddy.git
   cd AI-study-Buddy
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install crewai python-dotenv streamlit
   ```

4. Create a `.env` file in the root directory:
   ```env
   OPENAI_API_BASE=http://localhost:11434/v1
   OPENAI_MODEL_NAME=ollama/mistral
   OPENAI_API_KEY=local
   ```

---

## 🚀 Running the Project

### Interactive Web UI (Recommended)
Launch the beautiful Streamlit dark-mode interface:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### Command Line Interface
Alternatively, run the system directly in your terminal:
```bash
python main.py
```
