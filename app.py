import streamlit as st
import os
from groq import Groq
import random


def chat_with_groq(client,prompt,model):
    """
    This function sends a chat message to the Groq API and returns the content of the response.
    It takes three parameters: the Groq client, the chat prompt, and the model to use for the chat.
    """
    
    completion = client.chat.completions.create(
    model=model,
    messages=[
      {
            "role": "user",
            "content": prompt
        }
        ]
    )
  
    return completion.choices[0].message.content


def get_conversational_history(user_question_history,chatbot_answer_history,conversational_memory_length):
    """
    This function generates a full prompt for the chatbot based on the history of the conversation.
    It takes three parameters: the history of user questions, the history of chatbot answers, and the length of the conversational memory.

    Parameters:
    user_question_history (list): The history of user questions.
    chatbot_answer_history (list): The history of chatbot answers.
    conversational_memory_length (int): The length of the conversational memory.

    Returns:
    str: The full prompt for the chatbot.
    """

    base_prompt = '''
    Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!
    '''
    user_question_history = user_question_history[conversational_memory_length * -1:]
    chatbot_answer_history = chatbot_answer_history[conversational_memory_length * -1:]
    if len(chatbot_answer_history) > 0:
        conversational_history = '''
        As a recap, here is the current conversation:
            
        ''' + "\n".join(f"Human: {q}\nAI: {a}" for q, a in zip(user_question_history, chatbot_answer_history))

        full_prompt = base_prompt + conversational_history + '''
            Human: {user_question}
            AI:
        '''.format(user_question = user_question_history[-1])
    else:
        full_prompt = base_prompt + '''
            Human: {user_question}
            AI:
        '''.format(user_question = user_question_history[-1])
    
    return full_prompt


def get_random_prompt(file_path):
    """
    This function reads a file of prompts and returns a random prompt.
    """

    with open(file_path, 'r') as f:
        prompts = f.readlines()
    return random.choice(prompts).strip()


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # Initialize Groq client
    groq_api_key = os.environ['GROQ_API_KEY']
    client = Groq(
        # This is the default and can be omitted
        api_key=groq_api_key,
        base_url="https://api.groqcloud.com"
    )

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')

    # The title and greeting message of the Streamlit application
    st.title("Chat with Groq!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # Add customization options to the sidebar
    st.sidebar.title('Customization')
    additional_context = st.sidebar.text_input('Enter additional summarization context for the LLM here (i.e. write it in spanish):')
    model = st.sidebar.selectbox(
        'Choose a model',
        ['mixtral-8x7b-32768', 'llama2-70b-4096']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

    # The user is prompted to ask a question. The default value is a random prompt from the 'starter_prompts.txt' file.
    user_question = st.text_input("Ask a question:",value=get_random_prompt('starter_prompts.txt'))

    # If there is no user question history in the session state, an empty list is initialized.
    if 'user_question_history' not in st.session_state:
        st.session_state['user_question_history'] = []

    # If there is no chatbot answer history in the session state, an empty list is initialized.
    if 'chatbot_answer_history' not in st.session_state:
        st.session_state['chatbot_answer_history'] = []

    # If the user has asked a question,
    if user_question:
        # The question is added to the user question history.
        st.session_state['user_question_history'].append(user_question)

        # The full prompt for the chatbot is generated based on the conversational history.
        conversational_history_question = get_conversational_history(st.session_state['user_question_history'],st.session_state['chatbot_answer_history'],conversational_memory_length)
        
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        llm_answer = chat_with_groq(client,conversational_history_question,model)
        
        # The chatbot's answer is added to the chatbot answer history.
        st.session_state['chatbot_answer_history'].append(llm_answer)
        
        # The chatbot's answer is displayed.
        st.write("Chatbot:", llm_answer)

if __name__ == "__main__":
    main()







random_prompt = get_random_prompt('starter_prompts.txt')
print(random_prompt)