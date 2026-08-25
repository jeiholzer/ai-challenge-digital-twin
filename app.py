import os 
from openai import OpenAI
import gradio as gr

#------------------------------------
#   SETUP
#------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
	raise Exception("OPENAI_API_KEY environment variable is not set.")
else:
	print(OPENAI_API_KEY[:8] + "..." + OPENAI_API_KEY[-8:])  # Print first and last 8 characters of the API key for verification

client = OpenAI()


#-----------------------------------
# Load a document
#-----------------------------------
document_overview = """
My name is Joel Eiholzer
I live in southwestern Virginia, USA. I am a software engineer with a passion for AI and machine learning. I have experience in developing web applications, data analysis, and cloud computing. 
I enjoy learning new technologies and applying them to solve real-world problems.
20+ years of experience as a Project Manager and Software Developer, managing IT projects with an eye towards continuous process improvement. Project leadership of cross-functional remote teams, fostering team coordination through a culture of inclusion, prioritizing collaboration both within my team and outside the team. Eﬀective at collaboration with diverse personalities
I have run several marathons and triathlons. One day, I decided I wanted to be able to say I had run a marathon, so I made a plan and ran my first marathon in Columbus, Ohio. After a while, I got tired of just running, so I decided to try a triathlon. My first triathlon was at Clemson University in South Carolina.
"""


#-----------------------------------
# System Message
#-----------------------------------
# this is not necessary but might be worth it
system_message = "You are a helpful assistant that answers questions based on the provided content.\
	If you don't know the answer, say that you don't know. Always use all available information to provide\
	the best answer. Important: do not talk about any topics that are not in the provided context.\
	And only use the information provided in the context to answer the question. If the question is not related\
	to the content, say you don't know\
	Keep your answers somewhat concise. If they want more information on something, you tell them they can ask a follow-up question"

#-----------------------------------
# Main Response function
#-----------------------------------
def response_ai(message,history):
	system_message_enhanced = system_message + "\n\nContect:\n" + document_overview

	# as usual
	message_to_llm = [{"role": "system", "content": system_message_enhanced}] + history + [{"role": "user", "content": message}]

	llm_response = client.chat.completions.create(
		model="gpt-4.1-mini",
		messages=message_to_llm
	)

	llm_message = llm_response.choices[0].message

	return(llm_message.content)

#-----------------------------------
# Launch Gradio
#-----------------------------------
gr.ChatInterface(
	fn=response_ai,
	title="Joel's first digital twin",
	chatbot=gr.Chatbot(),
	description="Chat with my twin online"
).launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT",7860)))























