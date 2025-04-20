import streamlit as st
from groq import Groq
from langchain.schema import AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate

# Clé API Groq (Remplace par ta clé API)
API_KEY = "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"
client = Groq(api_key=API_KEY)

def query_groq_api(user_message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Vous êtes un assistant utile, et vous devez toujours répondre en français."},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erreur : {str(e)}"

# LangChain wrapper
class GroqLLM(LLM):
    def _call(self, prompt, stop=None):
        return query_groq_api(prompt)

    @property
    def _identifying_params(self):
        return {"name": "GroqLLM"}

    @property
    def _llm_type(self):
        return "custom_groq"

# Définir le modèle de prompt
prompt = PromptTemplate(
    input_variables=["user_message"],
    template="Vous êtes un assistant utile, répondez à la requête suivante en arabe : {user_message}"
)

memory = ConversationBufferMemory(memory_key="chat_history")
llm_chain = LLMChain(llm=GroqLLM(), prompt=prompt, memory=memory)

# Menu des plats
menu = {
    "Curry de légumes": {"type": "végétarien", "épices": "moyen", "ingrédients": ["légumes", "curry", "riz basmati"]},
    "Pizza Margarita": {"type": "végétarien", "épices": "doux", "ingrédients": ["tomates", "mozzarella", "basilic"]},
    "Poulet épicé": {"type": "non-végétarien", "épices": "fort", "ingrédients": ["poulet", "épices", "riz"]},
    "Salade César": {"type": "végétarien", "épices": "doux", "ingrédients": ["salade", "poulet", "fromage", "croutons"]},
}

# Styles CSS personnalisés pour la discussion
st.markdown("""
    <style>
    .chat-container {
        width: 100%;
        max-width: 700px;
        margin: 0 auto;
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    .user-message {
        text-align: right;
        margin-bottom: 10px;
    }
    .bot-message {
        text-align: left;
        margin-bottom: 10px;
    }
    .message-box {
        display: inline-block;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
    }
    .user-message .message-box {
        background-color: #e0e0e0;
        color: #000;
    }
    .bot-message .message-box {
        background-color: #007bff;
        color: white;
    }
    .message-input {
        margin-top: 20px;
    }
    .container {
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007bff;'>Assistant de Commande 🤖</h1>", unsafe_allow_html=True)
st.write("Discutez avec un assistant IA")

# Initialiser les messages si ce n'est pas déjà fait
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fonction pour afficher la conversation comme une messagerie
def display_conversation():
    for i in range(0, len(st.session_state.messages), 2):
        if i < len(st.session_state.messages):
            user_msg = st.session_state.messages[i]
            st.markdown(f"""
                <div class="user-message">
                    <div class="message-box">
                        👤 {user_msg.content}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if i+1 < len(st.session_state.messages):
            bot_msg = st.session_state.messages[i+1]
            st.markdown(f"""
                <div class="bot-message">
                    <div class="message-box">
                        🤖 {bot_msg.content}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Afficher la conversation actuelle
display_conversation()

# Champ de texte pour l'entrée utilisateur
user_input = st.text_input("Votre message :", key="input_message", placeholder="Écrivez ici...")

if user_input:
    # Enregistrer le message utilisateur
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Vérifier si une réponse a déjà été générée pour cette entrée
    if "bot_response" not in st.session_state:
        # Générer la réponse du bot
        bot_response = llm_chain.run(user_message=user_input)

        # Recommandation personnalisée
        if "végétarien" in user_input.lower():
            recommended_dishes = [dish for dish, details in menu.items() if details["type"] == "végétarien"]
        elif "épicé" in user_input.lower():
            recommended_dishes = [dish for dish, details in menu.items() if details["épices"] == "fort"]
        else:
            recommended_dishes = list(menu.keys())

        # Créer le message de recommandation
        recommendations = f"Voici quelques suggestions pour vous : {', '.join(recommended_dishes)}."

        full_bot_message = f"{bot_response}\n\n{recommendations}"

        # Ajouter la réponse du bot
        st.session_state.messages.append(AIMessage(content=full_bot_message))
        # Marquer la réponse comme générée pour éviter une répétition infinie
        st.session_state.bot_response = full_bot_message

    # Afficher la conversation mise à jour
    display_conversation()
