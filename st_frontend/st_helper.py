import streamlit as st

## app imports
from api_helper.serp_api import serp_api_caller
from seo.data_for_seo_api import get_keywords
from llm_keyword_fetcher.llm_generator import call_llm

### Uncomment import 'pdb' this to use debugger in the app
### Use this code in between any file or function to stop debugger at any point pdb.set_trace()
import pdb

def handle_success(result):
    print("Success:", result.data)

# Function to handle failure
def handle_failure(result):
    print("Failure:", result.data["error"]["message"])

def initialize_session_data():
    return {
        'question': "",
        'primary_keyword': "",
        'blog_words_limit': "",
        'urls': [],
        'additional_context': "",
        'selected_meta_keywords': [],
        'secondary_keywords': [],
        'selected_keywords': []
    }

def handle_urls():
    urls_str = st.text_input("Enter URLs (separated by commas):")
    if urls_str:
        urls_str = urls_str.strip()
        if urls_str:
            urls = [url.strip() for url in urls_str.split(",")]
            return urls
        else:
            st.warning("Please enter URLs separated by commas.")
    return []

def handle_serp_api(option, question, session_data):
    if option == 'Use Serpi Api' and question:
        return serp_api_caller(question)
    elif option == 'Use Custom Urls':
        return handle_urls()
    elif option == 'Use Both of them' and question:
        return (handle_urls() + serp_api_caller(question))
    else:
        st.write('No option selected')


def primary_details(session_data):
    st.title("Primary Details to generate a blog:")

    question = st.text_input("Enter your topic name:", session_data['question'])
    primary_keyword = st.text_input("Enter primary keyword:", session_data['primary_keyword'])

    blog_words_limit_options = ['500 - 1000', '1000 - 1500', '1500 - 2000', '2000 - 2500']
    blog_words_limit_index = blog_words_limit_options.index(session_data['blog_words_limit'] or '500 - 1000')

    blog_words_limit = st.radio('Blog size in number of words:', blog_words_limit_options, index=blog_words_limit_index)
    
    option = st.radio('Select an option:', ['Use Serpi Api', 'Use Custom Urls', 'Use Both of them'])

    if (session_data['urls'] == []) or (session_data['option'] != option):
        urls = handle_serp_api(option, question, session_data)
        if urls:
            session_data['urls'] = urls
    st.write(session_data['urls'])
    session_data['option'] = option

    if question and primary_keyword and st.button('Fetch Secondary keywords Using LLM:'):
        keywords = call_llm(question, primary_keyword)
        session_data['keywords'] = keywords

    if 'keywords' in session_data:
        st.write(f"Available keywords --> {session_data['keywords']}")

    if 'keywords' in session_data:
        # keywords_s = session_data['selected_meta_keywords']
        selected_meta_keywords = st.multiselect("Select Secondary Keywords", session_data['keywords'])
        if selected_meta_keywords:
            session_data['selected_meta_keywords'] = selected_meta_keywords
    selected_rows = ''
    if st.button("Fetch keywords from DataForSeo"):
        success_result = get_keywords(primary_keyword)
        if success_result.success:
            sec_keywords = success_result.data['data']
            session_data['sec_keywords'] = sec_keywords
            handle_success(success_result)
        else:
            handle_failure(success_result)
            st.write(f"No similar keywords found for your primary keyword on --> {primary_keyword}")

    if 'sec_keywords' in session_data:
        st.write('Select Secondary keywords:')
        selected_rows = st.data_editor(
            session_data['sec_keywords'],
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Your Keyword?",
                    help="Select your keywords!",
                    default=False,
                )
            },
            hide_index=True,
        )

        selected_rows = {key: [value[i] for i in range(len(value)) if selected_rows['Select'][i]] for key, value in selected_rows.items()}
        st.write('Selected keywords:')
        st.data_editor(
            selected_rows,
            hide_index=True,
            disabled=["Select"]
        )
        session_data['secondary_keywords'] = selected_rows
    
    if selected_rows:
        selected_keywords = set(selected_rows['keyword'] + list(session_data['selected_meta_keywords']) + list(session_data['selected_keywords']))
    else:
        selected_keywords = set(list(session_data['selected_meta_keywords']) + list(session_data['selected_keywords']))

    if st.button("Reset Selected keywords"):
        selected_rows['keyword'] = []
        session_data['selected_meta_keywords'] = []
        selected_keywords = []

    st.write(f"## Selected Meta Keywords :-->")
    st.write("<ul>", unsafe_allow_html=True)
    for keyword in selected_keywords:
        st.write(f"<li>{keyword}</li>",unsafe_allow_html=True)
    st.write("</ul>", unsafe_allow_html=True)

    session_data['selected_keywords'] = selected_keywords
    session_data['question'] = question
    session_data['primary_keyword'] = primary_keyword
    session_data['blog_words_limit'] = blog_words_limit

    return question, primary_keyword, blog_words_limit, session_data['urls']

def generate_structure_form(session_data):
    st.title("Generate Structure:")
    additional_context = st.text_area("Enter additional context for Structure:", session_data['additional_context'])
    session_data['additional_context'] = additional_context
    st.write(f"## Selected Meta Keywords :-->")
    st.write("<ul>", unsafe_allow_html=True)
    for keyword in session_data['selected_keywords']:
        st.write(f"<li>{keyword}</li>",unsafe_allow_html=True)
    st.write("</ul>", unsafe_allow_html=True)


def convert_to_title_case(input_string):
    words = input_string.split('_')
    capitalized_words = [word.capitalize() for word in words]
    result_string = ' '.join(capitalized_words)
    return result_string