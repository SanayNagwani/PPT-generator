# ==================== modules====================
import os
import time
import langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from tavily import TavilyClient
import pytesseract as pyt
import numpy as np
from langchain.agents import create_agent
import streamlit as st



#======================== APi'KEYS ===================================
GOOGLE_API_KEY = st.sidebar.text_input("GEMINI",type="password")
GROQ_API_KEY = st.sidebar.text_input("GROQ",type="password")
TAVILY_API_KEY =st.sidebar.text_input("TAVILY",type="password")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


ALL_API = [GOOGLE_API_KEY, GROQ_API_KEY, TAVILY_API_KEY]

if not all(ALL_API):
  st.sidebar.error("PASS API_KEYS")

elif all(ALL_API):
  model = ChatGoogleGenerativeAI(            # step 1: model call
      model = "gemini-3.5-flash-lite",
      google_api_key = GOOGLE_API_KEY
  )
  
  st.sidebar.success("API KEYS LOADED SUCCESSFULLY")

elif any(ALL_API):
  st.sidebar.info("MUST PASS ALL API KEYS")

else:
  st.info("LOADED")


#=================== front end =============================
st.title("AI-AGENT-POWERED PPT GENERATOR")

user_query = st.text_area("Write your ppt topic or prompt: ")

#=======================ASSESTS=====================

# step 2: tools creation
# tool_1

def search_latest_info(query):
  """this function search latest
  news or content from website
  using tavily, helpful to check
  trending content"""

  client = TavilyClient(api_key= TAVILY_API_KEY)
  response = client.search(query)
  return response

# tool 2:
def generate_image(img_prompt):
    """this function helps to generate image
    using free api, with given
    img_prompt using pollinations"""
    
    url = f"https://image.pollinations.ai/{img_prompt}"
    #file handling
    import requests as r
    content = r.get(url).content
    with open(f"Image.jpeg",'wb') as f:
      f.write(content)
    
    from PIL import Image
    return url


#With tabs
tab1, tab2, tab3 = st.tabs(["GENERATE IMAGE",
                          "CHECK LATEST NEWS",
                          "GENERATE PPT"])


#===================ADVANCE ========================
  # detailed prompt generator
def prompt_generator(model, query):
  prompt = f"""your task is to give detailed prompt instructions
  for given

  prompt:
  you are a professiopnal PPT generator, where
  user will give the query and based on that,
  you have to generate dynamic , HTML output based
  PPT with advanced css and dynamic UI and UX with
  ppt toggle button, based on query take image reference to generate
  and embed the same in ppt, using
  Image ref: url = https://images.unsplash.com/photo, 
  or url = https://image.pollinations.ai/, 
  make sure img src must be valid, and image must be
  present inside html, Generate
  with image caption, and no markdowns
  user query given below:{query}
  """

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open("ppt_prompt.txt",'w') as f:
    f.write(final_prompt)
  return final_prompt


if all(ALL_API) and user_query:
       
  agent = create_agent(
      model = model,
      tools = [search_latest_info,
                generate_image]
                )
  
  #==================DISPLAY AGENT===================
  #st.sidebar.image(agent)
  
  #================WITH TABS========================
  with tab1:
    st.header("generative image give prompt")
    if st.button("CLICK TO GENERATE: ", key = "generate_img_button"):
      with st.spinner("Running agent"):
        data = f"https://image.pollinations.ai/{user_query}"
        time.sleep(3)
        st.image(data)
        # st.image("Image.jpeg")

  
  with tab2:
    st.header("check latest news")
    if st.button("Fetch news: ", key = "news_button"):
      with st.spinner("Running agent.."):
        
        prompt = """give latest news india or word news related 
        to tech, business, jobs, or user required output
        in proper HTML news templates""" + user_query
  
        response = agent.invoke({'messages':[{'role':"user",
                                              "content":prompt}]})
        code = response['messages'][-1].content[-1]['text']
  
        st.html(code, width="stretch",
                unsafe_allow_javascript=True)
        
  with tab3:
    st.header("Create PPT")
    if st.button("Click to generate: ", key = "generate_ppt_button"):
      with st.spinner("Running agent.."):
        final_propmt = prompt_generate(model,user_query)
  
        response = agent.invoke({'messages':[{'role':"user",
                                              "content":final_prompt}]})
        
        code = response['messages'][-1].content[-1]['text']
        st.html(code, width="stretch",
                unsafe_allow_javascript=True)
        if st.download_button(label="Download PPT",
            data=code,
            file_name="ppt.html",
            mime="text/html"):
  
  
          st.success("PPT downloaded Successfully!!")
