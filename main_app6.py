import pandas as pd
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
from models import faq_gpt, assistance_gpt, recommendation_gpt
import base64
from openai import OpenAI
from trulens_eval import Feedback, OpenAI as fOpenAI, Tru
from trulens_eval import TruBasicApp
import matplotlib.pyplot as plt
from pymongo import MongoClient
import sys
import path

dir = path.Path(__file__).abspath()
sys.path.append(dir.parent.parent)
API_KEY = 'API-KEY'
tru = Tru()
tru.reset_database()
fopenai = fOpenAI(api_key=API_KEY)
f_relevance = Feedback(fopenai.relevance).on_input_output()
tru_metric_faq = TruBasicApp(faq_gpt.predict, app_id="serv_faq", feedbacks=[f_relevance])
tru_metric_recommendation = TruBasicApp(recommendation_gpt.predict, app_id="serv_recom", feedbacks=[f_relevance])
tru_metric_assistance = TruBasicApp(assistance_gpt.predict, app_id="serv_assist", feedbacks=[f_relevance])
faq_df = pd.read_csv("chat_logs/faq_logs.csv")
recom_df = pd.read_csv("chat_logs/recom_logs.csv")
assist_df = pd.read_csv('chat_logs/assists_logs.csv')

model_state = "Assistance"


def show_main_app():
    def convert_audio_to_base64(audio_file_path):
        with open(audio_file_path, "rb") as audio_file:
            return base64.b64encode(audio_file.read()).decode('utf-8')

    def transcribe_text_to_voice(audio_location):
        client = OpenAI(api_key=API_KEY)
        audio_file = open(audio_location, "rb")
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

    def text_to_speech_ai(speech_file_path, api_response):
        client = OpenAI(api_key=API_KEY)
        response = client.audio.speech.create(model="tts-1", voice="nova", input=api_response)
        response.stream_to_file(speech_file_path)

    # Sidebar for direct model selection
    global tru, tru_metric_faq, tru_metric_assistance, tru_metric_recommendation, model_state
    with st.sidebar:
        st.header("Model Selection")
        model_type = st.selectbox(
            "Select Model Type",
            ("Assistance", "Recommendation", "F.A.Q"),  # Example model types
            index=0,  # Default to the first option
            help="Select the model to use for predictions."
        )
        model_state = model_type
        st.session_state.model_type = model_type
    st.title(model_type + " Mode", anchor=None)

    # Main layout: Use columns to split the screen into two main parts
    left_col, right_col = st.columns([4, 4])  # Adjust the ratio as needed
    audio_text = None
    with left_col:
        text_holder = st.empty()
        # Chat and response input area
        input_text = text_holder.text_area("Hey there! Let me know how can I help you?", key="query_input",
                                           help="Type your query here.")
        response_chat = {}
        audio_bytes = audio_recorder(text="Ask me", icon_size="2x")
        if audio_bytes:
            ##Save the Recorded File
            audio_location = "audio_file.wav"
            with open(audio_location, "wb") as f:
                f.write(audio_bytes)

            # Transcribe the saved file to text
            audio_text = transcribe_text_to_voice(audio_location)
            text_holder.write(audio_text)
        if st.button("Chat", key="predict_btn", help="Click here to get the prediction") or audio_text:
            if audio_text:
                input_text = audio_text
            if input_text:
                # Placeholder for the response
                response_placeholder = st.empty()

                with st.spinner('Athena Thinking...'):
                    # Simulated delay to fetch prediction
                    if model_type == "F.A.Q":
                        response_chat = faq_gpt.predict(input_text, "sdrwrewrewr")
                        with tru_metric_faq as recording:
                            tru_metric_faq.app(input_text, session_id="asda3423")
                        tru_df = tru.get_records_and_feedback(app_ids=[])[0]
                        tru_df = pd.DataFrame(tru_df,
                                              columns=["ts", "input", "output", "record_id", "relevance", "latency",
                                                       "total_tokens", "total_cost"])
                        df = pd.concat([faq_df, tru_df], ignore_index=True)
                        df.to_csv("chat_logs/faq_logs.csv", index=False)
                    elif model_type == "Recommendation":
                        response_chat = recommendation_gpt.predict(input_text, "sdrwrewrewr")
                        with tru_metric_recommendation as recording:
                            tru_metric_recommendation.app(input_text, session_id="asda3423")
                        tru_df = tru.get_records_and_feedback(app_ids=[])[0]
                        tru_df = pd.DataFrame(tru_df,
                                              columns=["ts", "input", "output", "record_id", "relevance", "latency",
                                                       "total_tokens", "total_cost"])
                        df = pd.concat([recom_df, tru_df], ignore_index=True)
                        df.to_csv("chat_logs/recom_logs.csv", index=False)
                    elif model_type == "Assistance":
                        response_chat = assistance_gpt.predict(input_text, "sdrwrewrewr")
                        with tru_metric_assistance as recording:
                            tru_metric_assistance.app(input_text, session_id="asda3423")
                        tru_df = tru.get_records_and_feedback(app_ids=[])[0]
                        tru_df = pd.DataFrame(tru_df,
                                              columns=["ts", "input", "output", "record_id", "relevance", "latency",
                                                       "total_tokens", "total_cost"])
                        df = pd.concat([assist_df, tru_df], ignore_index=True)
                        df.to_csv("chat_logs/assists_logs.csv", index=False)
                if 'audio_version' not in st.session_state:
                    st.session_state['audio_version'] = 0  # Initialize the version
                st.session_state['audio_version'] += 1
                speech_file_path = f'audio_response.mp3'
                text_to_speech_ai(speech_file_path, response_chat.get("answer", "No response"))
                # Display the response with increased font size
                response_placeholder.markdown(
                    f'<p style="font-size: 20px;">Athena: {response_chat.get("answer", "No response")}</p>',
                    unsafe_allow_html=True)
                # st.markdown(audio_html, unsafe_allow_html=True)
                st.audio(speech_file_path)
                if model_type == "F.A.Q":
                    with tru_metric_faq as recording:
                        tru_metric_faq.app(input_text, session_id="asda3423")
                    tru_df = tru.get_records_and_feedback(app_ids=[])[0]
                    tru_df = pd.DataFrame(tru_df, columns=["ts", "input", "output", "record_id", "relevance", "latency",
                                                           "total_tokens", "total_cost"])
                    tru_df["Athena"] = response_chat.get("answer", "No response")

                    df = pd.concat([faq_df, tru_df], ignore_index=True)
                    df.to_csv("chat_logs/faq_logs.csv", index=False)
                elif model_type == "Recommendation":
                    with tru_metric_recommendation as recording:
                        tru_metric_recommendation.app(input_text, session_id="asda3423")
                    tru_df = tru.get_records_and_feedback(app_ids=[])[0]
                    tru_df = pd.DataFrame(tru_df, columns=["ts", "input", "output", "record_id", "relevance", "latency",
                                                           "total_tokens", "total_cost"])
                    tru_df["Athena"] = response_chat.get("answer", "No response")

                    df = pd.concat([recom_df, tru_df], ignore_index=True)
                    df.to_csv("chat_logs/recom_logs.csv", index=False)
                elif model_type == "Assistance":
                    with tru_metric_assistance as recording:
                        tru_metric_assistance.app(input_text, session_id="asda3423")
                    tru_df = tru.get_records_and_feedback(app_ids=[])[0]
                    tru_df = pd.DataFrame(tru_df, columns=["ts", "input", "output", "record_id", "relevance", "latency",
                                                           "total_tokens", "total_cost"])
                    tru_df["Athena"] = response_chat.get("answer", "No response")
                    df = pd.concat([assist_df, tru_df], ignore_index=True)
                    df.to_csv("chat_logs/assists_logs.csv", index=False)
            else:
                st.error("Please enter some text to get a prediction.")

    with right_col:
        # Placeholder for the image or a simulated image fetch/display
        image_placeholder = st.empty()
        image_path = "Athena.png"
        image = Image.open(image_path)
        image_placeholder.image(image, caption="Hi, I'm Athena", use_column_width=True)
        try:
            img_url = response_chat.get("img_url", None)
            if img_url:
                response = requests.get(img_url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                image_placeholder.image(img, caption=response_chat.get("art_name", ""), use_column_width='always')

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching image: {e}")
        except IOError as e:
            st.error(f"Error displaying image: {e}")


# Define a function for the content of plot_test.py
def show_plot_test():
    with st.sidebar:
        st.header("Analytics Dashboard")
        model_state = st.selectbox(
            "Select Mode",
            ("Assistance", "Recommendation", "F.A.Q"),
            index=0,
            help="Select the model to use for predictions."
        )
    mgdb_client = MongoClient('mongo_url')
    product_categories = None
    catagory_type = None
    collection = None
    if model_state == "Assistance":
        df = pd.read_csv("chat_logs/assists_logs.csv")
        db = mgdb_client["store_product_demo"]
        collection = db.product_list_v6
        product_categories = collection.distinct('Category')
        catagory_type = "Product "
    elif model_state == "Recommendation":
        df = pd.read_csv("chat_logs/recom_logs.csv")
        db = mgdb_client["abbozzo_v4"]
        collection = db.art_data
        product_categories = ['aquatint', 'limestone', 'spray paint', 'linen', 'ceramic', 'woodblock', 'collage',
                              'print', 'triptych', 'crayon', 'bronze', 'pastel', 'acrylic', 'brass', 'cotton',
                              'graphite', 'encaustic', 'pearl', 'plaster', 'board', 'watercolour', 'mezzotint',
                              'magazine', 'canvas', 'soapstone', 'japanese', 'mixed media', 'fine art', 'paper',
                              'etching', 'antique', 'ink', 'resin', 'diptych', 'gesso', 'plexiglass', 'cement', 'wax',
                              'quadriptych', 'liquitex', 'rag', 'photograph', 'silver leaf', 'panel', 'monoprint',
                              'acid free', 'gold', 'glass', 'aluminum', 'pigment ink', 'wood', 'marble', 'oil']

        catagory_type = "Art "

    elif model_state == "F.A.Q":
        df = pd.read_csv("chat_logs/faq_logs.csv")
    out_answer = df["output"]
    print(model_state)
    if product_categories is not None:
        category_count = {category: 0 for category in product_categories}
        st.markdown("<h1 style='text-align: center; color: white;'>Athena's Log Analysis Breakdown</h1>",
                    unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: white;'>Visual Analysis</h3>", unsafe_allow_html=True)

        def count_category_occurrences(sentence, categories):
            sentence_lower = sentence.lower()
            for category in categories:
                if category.lower() in sentence_lower:
                    category_count[category] += 1

        for answer in out_answer:
            count_category_occurrences(answer, product_categories)

        df_category_counts = pd.DataFrame(list(category_count.items()), columns=['Category', 'Count'])

        df_category = df_category_counts.sort_values(by='Count', ascending=False)

        top_5_categories = df_category.head(5)

        def create_pie_chart(data, labels, title):
            fig, ax = plt.subplots()
            explode_values = [0.05] * len(data)  # Adjust this value as needed
            ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=140, shadow=True,
                   explode=explode_values, textprops={'color': "white", 'fontsize': 10, 'fontweight': 'bold'})
            ax.set_title(title, fontsize=14, fontweight='bold', color='white')
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0.0)
            ax.set_facecolor('none')
            return fig

        def create_horizontal_bar_graph(df, title, xlabel, ylabel):
            plt.style.use('ggplot')
            title_font = {'fontsize': 16, 'fontweight': 'bold'}
            label_font = {'fontsize': 12, 'fontweight': 'bold'}
            ticks_font = {'labelsize': 10}

            fig, ax = plt.subplots(figsize=(10, 8))

            bars = ax.barh(df['Category'], df['Count'], color=plt.cm.tab20c.colors[:len(df)])

            for bar in bars:
                ax.text(
                    bar.get_width(),
                    bar.get_y() + bar.get_height() / 2,
                    f'{bar.get_width()}',
                    va='center',
                    fontweight='bold',
                    color='white'
                )
            ax.set_title(title, **title_font, color='white')
            ax.set_xlabel(xlabel, **label_font, color='white')  # Set x-axis label color to white
            ax.set_ylabel(ylabel, **label_font, color='white')

            # Set the tick labels with the fontdict
            ax.tick_params(axis='x', colors='white', labelsize=12)  # X-axis tick labels
            ax.tick_params(axis='y', colors='white', labelsize=12)

            # Remove all spines
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)

            # Remove x, y Ticks
            ax.xaxis.set_ticks_position('none')
            ax.yaxis.set_ticks_position('none')

            # Add padding between axes and labels
            ax.xaxis.set_tick_params(pad=5, **ticks_font)
            ax.yaxis.set_tick_params(pad=10, **ticks_font)

            # Add x, y gridlines
            ax.grid(True, color='white', linestyle='-.', linewidth=0.5, alpha=0.6)

            # Show top values
            ax.invert_yaxis()

            # Remove background color
            ax.set_facecolor('none')
            fig.patch.set_alpha(0.0)

            # Adjust layout to make sure everything fits
            plt.tight_layout()

            return fig

        # Using Streamlit's columns to layout the pie chart and horizontal bar graph with space in between
        col1, spacer, col2 = st.columns([1, 0.1, 1])

        with col1:
            st.pyplot(create_pie_chart(df_category['Count'], df_category['Category'], f'{catagory_type} Category'))

        with col2:
            # Create and display the horizontal bar graph
            fig = create_horizontal_bar_graph(top_5_categories, f'Top 5 {catagory_type} Categories', 'Category',
                                              'Count')
            st.pyplot(fig)

    # Display the wide DataFrame below the pie charts
    # st.header("Athena's Assistance Chat Logs")
    if model_state == "Assistance":
        st.markdown("<h1 style='text-align: center; color: white;'>Athena's Assistance Chat Logs</h1>",
                    unsafe_allow_html=True)
    elif model_state == "Recommendation":
        st.markdown("<h1 style='text-align: center; color: white;'>Athena's Recommendation Chat Logs</h1>",
                    unsafe_allow_html=True)
    elif model_state == "F.A.Q":
        st.markdown("<h1 style='text-align: center; color: white;'>Athena's F.A.Q Chat Logs</h1>",
                    unsafe_allow_html=True)

    df = pd.DataFrame(df, columns=["ts", "Athena", "input", "output", "relevance", "latency"])
    df.rename(columns={'ts': 'time', 'input': 'Question', "Athena":"Athena's Answer",'output': 'Trulens'}, inplace=True)
    df = df.drop_duplicates(subset=['Trulens'])

    st.dataframe(df)


if 'page' not in st.session_state:
    st.session_state.page = 'Main App'

# Conditionally display buttons in the sidebar based on the current page
if st.session_state.page == 'Main App':
    if st.sidebar.button('Analytics Dashboard'):
        st.session_state.page = 'Plot Test'
    show_main_app()
elif st.session_state.page == 'Plot Test':
    if st.sidebar.button('Back to Chat Screen'):
        st.session_state.page = 'Main App'
    show_plot_test()
