import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {
        "full_name": None,
        "email": None,
        "phone": None,
        "experience": None,
        "position": None,
        "location": None,
        "tech_stack": None,
        "questions_answered": 0,
        "total_questions": 0
    }

if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = "greeting"

if "current_questions" not in st.session_state:
    st.session_state.current_questions = []

def get_fallback_questions(tech_stack):
    """Generate fallback questions when API is unavailable"""
    questions = {
        "python": [
            "1. Explain the difference between lists and tuples in Python. When would you use each?",
            "2. What are decorators in Python? Provide an example of how you would use them.",
            "3. Explain the concept of generators in Python and when you would use them.",
            "4. How do you handle exceptions in Python? Provide an example.",
            "5. What is the difference between 'is' and '==' in Python?"
        ],
        "mysql": [
            "1. Explain the difference between INNER JOIN and LEFT JOIN in MySQL.",
            "2. What are indexes in MySQL and when would you use them?",
            "3. How do you optimize a slow-running query in MySQL?",
            "4. Explain the concept of transactions in MySQL.",
            "5. What are the different types of MySQL storage engines and their use cases?"
        ]
    }
    
    tech_list = [tech.strip().lower() for tech in tech_stack.split(',')]
    all_questions = []
    
    for tech in tech_list:
        if tech in questions:
            all_questions.extend(questions[tech])
    
    return all_questions

def get_ai_response(messages, max_retries=3):
    """Get response from OpenRouter API with retry logic"""
    for attempt in range(max_retries):
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://talentscout.com",  # Replace with your site URL
                "X-Title": "TalentScout Hiring Assistant"  # Replace with your site name
            }
            
            data = {
                "model": "qwen/qwen3-235b-a22b:free",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                OPENROUTER_API_URL, 
                headers=headers, 
                json=data,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                st.warning("API request timed out. Using fallback questions.")
                return None
            time.sleep(1)
        except Exception as e:
            if attempt == max_retries - 1:
                st.warning(f"Error: {str(e)}. Using fallback questions.")
                return None
            time.sleep(1)
    return None

def validate_input(input_type, value):
    """Validate user input based on type"""
    if input_type == "email":
        return "@" in value and "." in value
    elif input_type == "phone":
        return any(c.isdigit() for c in value)
    elif input_type == "experience":
        try:
            years = float(value)
            return 0 <= years <= 50
        except:
            return False
    return True

def get_fallback_response():
    """Generate a fallback response when input is not understood"""
    fallback_messages = [
        "I'm not sure I understand. Could you please rephrase that?",
        "I didn't quite catch that. Could you try again?",
        "I'm having trouble understanding. Could you be more specific?",
        "I'm not sure what you mean. Could you clarify?"
    ]
    return fallback_messages[hash(datetime.now().strftime("%S")) % len(fallback_messages)]

def initialize_conversation():
    """Initialize the conversation with a greeting"""
    greeting = """Hello! Welcome to TalentScout, your intelligent hiring assistant. 
    I'll help gather your details and ask a few technical questions to get started. 
    You can type 'exit' anytime to end the chat.
    
    Let's begin! What is your full name?"""
    
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.conversation_state = "collecting_name"

def generate_technical_questions(tech_stack):
    """Generate technical questions based on tech stack"""
    prompt = f"""As a technical interviewer, generate 3-5 specific technical interview questions for each technology in this stack: {tech_stack}
    
    For each technology:
    1. Include questions of varying difficulty (basic to advanced)
    2. Focus on practical knowledge and problem-solving
    3. Include questions about best practices and common pitfalls
    4. Format each question with a clear number and technology label
    
    Example format:
    Python:
    1. [Question about Python]
    2. [Question about Python]
    
    Django:
    1. [Question about Django]
    2. [Question about Django]
    """
    
    messages = [
        {"role": "system", "content": "You are a senior technical interviewer with expertise in software development and system design."},
        {"role": "user", "content": prompt}
    ]
    
    questions = get_ai_response(messages)
    
    if questions is None:
        # Use fallback questions if API fails
        questions = get_fallback_questions(tech_stack)
        st.session_state.current_questions = questions
    else:
        st.session_state.current_questions = questions.split('\n\n')
    
    st.session_state.candidate_info["total_questions"] = len(st.session_state.current_questions)
    st.session_state.messages.append({"role": "assistant", "content": "\n".join(st.session_state.current_questions)})
    st.session_state.messages.append({"role": "assistant", "content": "Please answer these questions one by one. You can start with the first question."})

def process_user_input(user_input):
    """Process user input based on conversation state"""
    if user_input.lower() in ['exit', 'quit', 'bye']:
        end_conversation()
        return

    if st.session_state.conversation_state == "collecting_name":
        if len(user_input.strip()) < 2:
            st.session_state.messages.append({"role": "assistant", "content": "Please provide your full name."})
            return
        st.session_state.candidate_info["full_name"] = user_input
        st.session_state.messages.append({"role": "assistant", "content": "Great! What is your email address?"})
        st.session_state.conversation_state = "collecting_email"
    
    elif st.session_state.conversation_state == "collecting_email":
        if not validate_input("email", user_input):
            st.session_state.messages.append({"role": "assistant", "content": "Please provide a valid email address."})
            return
        st.session_state.candidate_info["email"] = user_input
        st.session_state.messages.append({"role": "assistant", "content": "What is your phone number?"})
        st.session_state.conversation_state = "collecting_phone"
    
    elif st.session_state.conversation_state == "collecting_phone":
        if not validate_input("phone", user_input):
            st.session_state.messages.append({"role": "assistant", "content": "Please provide a valid phone number."})
            return
        st.session_state.candidate_info["phone"] = user_input
        st.session_state.messages.append({"role": "assistant", "content": "How many years of experience do you have?"})
        st.session_state.conversation_state = "collecting_experience"
    
    elif st.session_state.conversation_state == "collecting_experience":
        if not validate_input("experience", user_input):
            st.session_state.messages.append({"role": "assistant", "content": "Please provide a valid number of years of experience."})
            return
        st.session_state.candidate_info["experience"] = user_input
        st.session_state.messages.append({"role": "assistant", "content": "Which position(s) are you interested in?"})
        st.session_state.conversation_state = "collecting_position"
    
    elif st.session_state.conversation_state == "collecting_position":
        st.session_state.candidate_info["position"] = user_input
        st.session_state.messages.append({"role": "assistant", "content": "Where are you currently located?"})
        st.session_state.conversation_state = "collecting_location"
    
    elif st.session_state.conversation_state == "collecting_location":
        st.session_state.candidate_info["location"] = user_input
        st.session_state.messages.append({"role": "assistant", "content": "Please list your tech stack (e.g., Python, Django, React, MySQL, Docker). Be specific about the technologies you're proficient in."})
        st.session_state.conversation_state = "collecting_tech_stack"
    
    elif st.session_state.conversation_state == "collecting_tech_stack":
        st.session_state.candidate_info["tech_stack"] = user_input
        generate_technical_questions(user_input)
        st.session_state.conversation_state = "asking_technical_questions"
    
    elif st.session_state.conversation_state == "asking_technical_questions":
        handle_technical_question_response(user_input)

def handle_technical_question_response(user_input):
    """Handle responses to technical questions"""
    st.session_state.candidate_info["questions_answered"] += 1
    
    if st.session_state.candidate_info["questions_answered"] >= st.session_state.candidate_info["total_questions"]:
        end_conversation()
    else:
        next_question = st.session_state.current_questions[st.session_state.candidate_info["questions_answered"]]
        st.session_state.messages.append({"role": "assistant", "content": f"Thank you for your answer. Here's the next question:\n\n{next_question}"})

def end_conversation():
    """End the conversation gracefully"""
    summary = f"""Thank you for your time, {st.session_state.candidate_info['full_name']}! 
    
    Here's a summary of your information:
    - Position: {st.session_state.candidate_info['position']}
    - Experience: {st.session_state.candidate_info['experience']} years
    - Tech Stack: {st.session_state.candidate_info['tech_stack']}
    
    We'll review your responses and contact you at {st.session_state.candidate_info['email']} about the next steps in the hiring process.
    
    Have a great day!"""
    
    st.session_state.messages.append({"role": "assistant", "content": summary})
    st.session_state.conversation_state = "ended"

def main():
    st.title("TalentScout Hiring Assistant")
    
    # Initialize conversation if not started
    if not st.session_state.messages:
        initialize_conversation()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if st.session_state.conversation_state != "ended":
        user_input = st.chat_input("Type your message here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            process_user_input(user_input)
            st.experimental_rerun()

if __name__ == "__main__":
    main() 