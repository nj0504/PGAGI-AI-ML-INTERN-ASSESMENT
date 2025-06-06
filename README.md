# TalentScout Hiring Assistant

An intelligent chatbot designed to assist in the initial screening of candidates for technology positions. The chatbot gathers essential information and generates relevant technical questions based on the candidate's declared tech stack.

## Features

- Interactive chat interface using Streamlit
- Step-by-step information gathering
- Dynamic technical question generation based on tech stack
- Context-aware conversation flow
- Graceful conversation ending

## Prerequisites

- Python 3.8 or higher
- Qwen API key (included in the code)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd talentscout
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Interact with the chatbot:
   - Follow the prompts to provide your information
   - Type 'exit', 'quit', or 'bye' to end the conversation
   - Answer the technical questions generated based on your tech stack

## Project Structure

```
talentscout/
│
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technical Details

- **Frontend**: Streamlit
- **AI Model**: Qwen 3 235B
- **State Management**: Streamlit session state
- **Data Handling**: In-memory storage (simulated)

## Prompt Engineering

The chatbot uses carefully crafted prompts to:
1. Guide the conversation flow
2. Collect candidate information systematically
3. Generate relevant technical questions based on the tech stack
4. Maintain context throughout the conversation

## Challenges & Solutions

1. **Context Management**
   - Solution: Implemented state management using Streamlit's session state
   - Tracks conversation progress and candidate information

2. **Technical Question Generation**
   - Solution: Uses Qwen API with specific prompts to generate relevant questions
   - Questions are tailored to the candidate's tech stack

3. **User Experience**
   - Solution: Clean, intuitive interface with clear prompts
   - Graceful handling of conversation flow and exit conditions

## Future Enhancements

- Integration with a database for persistent storage
- Sentiment analysis of candidate responses
- Multilingual support
- Advanced UI customization
- Integration with applicant tracking systems

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 