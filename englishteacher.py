# projeto báscio desenvolvido para aprendizado em Python - Por Izabelli Soriano

import os
import streamlit as st
import google.generativeai as genai

#Configuração da página com o Streamlit
st.set_page_config(
    page_title="English Teacher", 
    page_icon=":books:", 
    layout="centered",
    initial_sidebar_state="expanded"
)

#Definição do prompt para o funcionamento do sistema
CUSTOM_PROMPT = """
Você é um professor de inglês, um assistente de IA especialista em ensino de língua inglesa, Sua missão é ajudar o usuário a aprender inglês de forma ativa, clara e progressiva, desenvolvendo fala, escrita, compreensão e vocabulário.

REGRAS DE OPERAÇÃO:
1.  **Foco exclusivo em ensino de inglês**: Responda apenas a perguntas relacionadas ao aprendizado em inglês. Se o usuário fugir do tema, responda educadamente e redirecione para o aprendizado da língua.
2.  **Estrutura da Resposta**: Sempre formate suas respostas da seguinte maneira:
    * **Explicação Clara**: Explique o conceito de forma clara e simples em inglês. De forma clara, como se fosse para uma pessoa leiga no assunto ou até mesmo para uma criança.
    * **Exemplo**: Forneça exemplos práticos de frases: Frases do dia a dia, expressões comuns, ou situações cotidianas onde o conceito é aplicado.
    * **Prática**: Proponha exercícios para o usuário:Perguntas abertas, Traduções, Completar frases, Reformular ideias.
    * **Correction**: Quando necessário corrija erros, Explique o erro de forma simples e clara.forneça a versão correta.
    **Estilo de ensino**: Conduza a conversa principalmente em inglês. Use português apenas quando necessário para destravar entendimento. Seja didático, direto e progressivo.Faça perguntas com frequência para estimular resposta ativa. Não responda pelo o usuário, incentive-o a pensar e formular suas próprias respostas. Mantenha um tom amigável encorajador e paciente. Adapte o nível de complexidade conforme o progresso do usuário, começando com conceitos básicos e avançando gradualmente para tópicos mais complexos.
"""

#Ajustando a barra lateral do Streamlit
with st.sidebar:
    st.title("English Teacher")
    st.markdown("Bem-vindo ao English Teacher! Este é um assistente de IA projetado para ajudar você a aprender inglês de forma ativa e progressiva. Sinta-se à vontade para fazer perguntas, praticar exercícios e melhorar suas habilidades em inglês. Vamos começar nossa jornada de aprendizado juntos!")

#Ajustando a Api do gemini    
    st.divider()
    gemini_api_key = st.text_input("Chave de API do Google Gemini:", type="password")
    if not gemini_api_key:
        st.info("Para interagir com o professor, insira sua chave de API. Clique em 'Create API key' no link a seguir para gerar uma gratuitamente: [Google AI Studio](https://aistudio.google.com/app/apikey).")

# Iniciar a variável do usuário
model = None

# Configurando a API do Gemini caso a chave seja fornecida
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        
        # Inicializando o modelo Gemini 2.5 Flash e passando as regras como system_instruction
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=CUSTOM_PROMPT
        )
    except Exception as e:
        st.error(f"Ocorreu um erro ao inicializar o Gemini. Verifique sua chave de API. Detalhes: {e}")

with st.sidebar:
    # Adiciona linhas divisórias e explicações extras na barra lateral
    st.markdown("---")
    st.markdown("Desenvolvido por Izabelli Soriano para auxiliar em suas dúvidas de aprendizado de inglês.")
    st.markdown("IA pode cometer erros. Sempre verifique as respostas.")
    st.link_button("Me siga no linkedin", "https://www.linkedin.com/in/izabellisoriano/")
    st.link_button("Meu github", "https://github.com/bellis0ri4ano")

#Titulo principal (agora fora do bloco if, para aparecer sempre)
st.title("English Teacher :books:") 
st.subheader("Seu assistente de aprendizado de inglês")
st.caption("Digite suas perguntas ou pratique exercícios para melhorar suas habilidades em inglês!")

# Inicializa o histórico de mensagens na sessão, caso ainda não exista
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe todas as mensagens anteriores armazenadas no estado da sessão
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caso não tenha chave, mas já existam mensagens, mostra aviso
if not model and st.session_state.messages:
    st.warning("Por favor, insira sua API Key do Google Gemini na barra lateral para continuar.")

# Captura a entrada do usuário no chat
if prompt := st.chat_input("What do you want to learn today? / Qual sua dúvida?"):
    
    # Se não houver modelo válido (chave não fornecida), mostra aviso e para a execução
    if not model:
        st.warning("Por favor, insira sua Chave de API do Gemini na barra lateral para começar.")
        st.stop()

    # Armazena a mensagem do usuário no estado da sessão
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibe a mensagem do usuário no chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepara o histórico para a API do Gemini (Converte 'assistant' para 'model')
    gemini_history = []
    # Pegamos todas as mensagens exceto a última (que acabou de ser inserida e será enviada como prompt)
    for msg in st.session_state.messages[:-1]:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # Cria a resposta do assistente no chat
    with st.chat_message("assistant"):
        with st.spinner("Thinking / Analisando sua pergunta..."):
            try:
                # Inicializa a sessão do chat com o histórico preparado
                chat_session = model.start_chat(history=gemini_history)
                
                # Chama a API do Gemini para gerar a resposta baseada no novo prompt
                response = chat_session.send_message(prompt)
                
                # Extrai a resposta gerada pela API
                ai_resposta = response.text
                
                # Exibe a resposta no Streamlit com efeito de máquina de escrever (opcional, aqui direto)
                st.markdown(ai_resposta)
                
                # Armazena resposta do assistente no estado da sessão
                st.session_state.messages.append({"role": "assistant", "content": ai_resposta})

            # Caso ocorra erro na comunicação com a API, exibe mensagem de erro
            except Exception as e:
                st.error(f"Ocorreu um erro ao se comunicar com a API do Gemini: {e}")

st.markdown(
    """
    <div style="text-align: center; color: gray; margin-top: 50px;">
        <hr>
        <p>English Teacher AI - Desenvolvido por Izabelli Soriano</p>
    </div>
    """,
    unsafe_allow_html=True
)
