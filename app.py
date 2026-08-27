import os 
from openai import OpenAI
import gradio as gr
import chromadb
import re
import uuid
import random
import json
import requests

#------------------------------------
#   SETUP
#------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
	raise Exception("OPENAI_API_KEY environment variable is not set.")
else:
	print(OPENAI_API_KEY[:8] + "..." + OPENAI_API_KEY[-8:])  # Print first and last 8 characters of the API key for verification

client = OpenAI()

pushover_url = "https://api.pushover.net/1/messages.json"
pushover_token = os.getenv("pushover_token")
pushover_user = os.getenv("pushover_user")

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

document_education = """
SUNY Canton - small two year college in upstate new you where I received an assocaites degree in Engineerign Science
Virginia Polytechnic Institute: a large university in southwestern virginia where I received my Bachelor of Science (BS) Degree in Computer Engineering
SSGI Agile Professional (SSGI-CAP)
SAFe 6 Scrum Master (SSM)
AWS Cloud Practitioner
PMI Generative AI Overview
AWS Certified AI Practitioner
Project Management Professional (PMP Certification)
AI Engineer Challenge 
"""

document_profesional_experience = """
ICF International | Project Manager	08/2019 - 06/2025
Responsible for ownership and full software development lifecycle of 6 technical projects included within the Housing and Urban Development HUD Exchange website (annual budget: $5M), while leading intuitive user-centered design efforts across the entire platform.
Key Accomplishments
•	Spearheaded a yearlong LMS migration that included a complete rebuild of the database, user interface, code, and SSO, plus successfully migrating 4,000 trainings, 100,000+ user accounts, and 700,000+ transcripts. 
•	Directed the shift from traditional hosting to an AWS data center platform, automating environment duplication and adhering to HUD security standards, resulting in annual savings of over $12,000.
•	Implemented process improvement, achieving near-zero site downtime within weeks by establishing a developer-led incident response model, cutting the average resolution time from 1.5 hours to under 30 minutes.
•	Orchestrated a comprehensive 3-month website redesign of 18,000+ web pages and 10 applications geared towards providing a better user experience.
•	Guided a six-month site search switch from Google Search Appliance to Elasticsearch/FESS, resulting in an estimated annual cost savings of $15,000 and increased search usage by 15%. 
•	Implemented the use of an Agile environment using both Scrum and Kanban methodologies.
Primary Responsibilities
•	Preside over multiple concurrent projects using Agile development, overseeing schedules, shifting project scope and priorities, managing budgets, mitigating risks with corrective action, and resource allocation.
•	Worked directly with clients to be their voice, gather technical specifications, and collect feedback on the success of products.
•	Coordinated daily with developers and BA’s on QA application testing.
•	Stakeholder management through weekly meetings for status reports on budget, development progress, scope, objectives, and timelines, enabling faster decision-making and smoother collaboration.
•	Work hand in hand with DevSecOps to deliver quality products in a safe and efficient manner.
Project Leadership
•	Acted as an intermediary between teams and non-technical stakeholders, negotiating and providing technical and non-technical translations between the two groups. 
•	Improved team development by assembling a team, assigning responsibilities, and empowering members to make decisions, resulting in a strong sense of responsibility in the final outcome.
•	Coached the professional development of direct reports, setting annual goals, conducting bi-weekly 1:1s, and delivering performance reviews.
•	Provided mentorship for several employees through a formal in-house career development program, guiding skill-building, goal-setting, and professional growth.

ICF International | Web Developer	03/2006 - 07/2019
Maintained websites for clients such as the US Air Force, the Department of Justice, the Department of Housing and Urban Development, the Department of Health and Human Services, and the State of Louisiana. 
Key Accomplishments
•	Developed original HUD Exchange Training component with integration between the HUD Exchange and SumTotal LMS, leveraging API calls and data exports, and implemented Single Sign-On (SSO) for seamless user access. 
•	Added the ability to relate questions in the HUD Exchange Ask A Question application.


Primary Responsibilities
•	Implemented new features and optimized the existing codebase, ensuring seamless performance and scalability.
•	Architected scalable database structures and engineered advanced SQL queries to support dynamic, data-driven web applications.

Internet Database | Project Manager	08/2005 - 02/2006
Responsible for managing product timelines and budgets, as well as enhancing and optimizing existing websites.
Primary Responsibilities
•	Worked closely with clients to gather requirements and maintain ongoing satisfaction throughout the product lifecycle. 
•	Built applications including a resume entry portal, invoicing system, and furniture management platform.
•	Coordinated with developers to ensure the timely delivery of client solutions aligned with specifications.

Automation Creations Inc | Web developer/Project Manager	06/1999 - 08/2005
Worked on the ALTESS Acquisition Information Management (AIM) system, a suite of applications with a $1 million annual development budget that collects acquisition program data from project managers reporting to U.S. Army leadership and the Office of the Secretary of Defense.
Key Accomplishments
•	Developed the initial version of the AIM system, architecting the database and coding core functionalities to support enterprise-level data collection and reporting.
•	Participated in status meetings with senior leadership, presenting updates on project progress, gathering high-level requirements, and discussing future planning.
•	Presented system improvements to audiences of hundreds at biannual conferences, demonstrating confident communication and subject matter expertise.
•	Delivered hands-on training sessions on the AIM suite to classroom groups of approximately 30 users, promoting practical understanding and confident system adoption.
Primary Responsibilities
•	Fostered effective collaboration between developers, DBAs, and testers by promoting open communication and shared accountability, ensuring smooth and timely product execution.
•	Oversaw all phases of AIM system development, from planning and architecture to implementation and delivery.
•	Work closely with customers through conferences, phone calls, and virtual meetings.
"""

document_technical_skills = """
Project Management Tools
Agile (Scrum, Kanban) · Risk Management · Scope Management · Stakeholder Engagement · Budgeting & Forecasting · Product Road mapping · Change Management · Human-Centered Design
Leadership & Collaboration
Cross-Functional Team Leadership · Remote Team Management · Mentorship & Coaching · Conflict Resolution · Emotional Intelligence · Strategic Communication · Adaptability · Inclusive Culture Building
Cloud & Technical Proficiency
AWS Cloud (EC2, Lambda, CloudFront, Kubernetes, DynamoDB) · DevOps, IaC, PaaS & SaaS · Adobe/SumTotal LMS Integration · Elasticsearch/FESS · ColdFusion · Lucee · JavaScript · MySQL · React · Docker
Tools & Platforms
Atlassian products JIRA and Confluence · MURAL · Slack · MS Teams · Trello · Zoom · Git/SVN · WordPress · Visio · PowerPoint · Excel
"""


#-----------------------------------
# Chunking function 
#-----------------------------------
def chunk_text(text, max_chars=300, min_chars=200, overlap=50):
    text = text.strip()
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + max_chars, text_len)

        if end < text_len:
            search_floor = start + min_chars
            end = find_break_point(text, search_floor, end)

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        next_start_target = max(start, end - overlap)
        start = find_forward_word_start(text, next_start_target, end)

    return chunks


def find_break_point(text, floor, ceiling):
    para_break = text.rfind('\n\n', floor, ceiling)
    if para_break != -1:
        return para_break + 2

    sentence_search_region = text[floor:ceiling]
    matches = list(re.finditer(r'[.!?](?=\s|$)', sentence_search_region))
    if matches:
        last = matches[-1]
        return floor + last.end()

    space = text.rfind(' ', floor, ceiling)
    if space != -1:
        return space + 1

    return ceiling


def find_forward_word_start(text, pos, limit):
    if pos >= limit:
        return limit

    if pos > 0 and not text[pos - 1].isspace() and not text[pos].isspace():
        next_space = text.find(' ', pos, limit)
        if next_space == -1:
            return limit
        pos = next_space + 1

    while pos < limit and text[pos].isspace():
        pos += 1

    return pos

#-----------------------------------
# RAG: Chunk, Embed & Store in ChromaDB
#-----------------------------------
documents = [
	{"text": document_education, "source": "Learning and Education"},
	{"text": document_profesional_experience, "source": "Work background and Professional Experience"},
	{"text": document_overview, "source": "General backgound and personal information"},
	{"text": document_technical_skills, "source": "Technical Skills and Proficiencies"}
]

chunks_list = []
ids = []
metadatas = []

for doc in documents:
	# prepare the list
	tmp_chunks_list = chunk_text(doc["text"])
	tmp_ids = [str(uuid.uuid4()) for _ in range(len(tmp_chunks_list))]
	tmp_metadatas = [{"source": doc["source"],"chunk_index":i} for i in range(len(tmp_chunks_list))]
	# add to main list
	chunks_list.extend(tmp_chunks_list)
	ids.extend(tmp_ids)
	metadatas.extend(tmp_metadatas)


embedding_response = client.embeddings.create(
	model="text-embedding-3-small",
	input=chunks_list
)
embeddings = [item.embedding for item in embedding_response.data]


chroma_client = chromadb.PersistentClient(path="./digital_twin_db")

# chroma_client.delete_collection("digital_twin") # used this to change the size of the embeddings, so we need to delete the collection and start over

# generally will just create but this way if you run the code again and the collection already exists it will return it and not error on create
chroma_collection = chroma_client.get_or_create_collection(name="digital_twin")
# generally will not do this but in case we run this again we want a clean slate
if chroma_collection.get()["ids"]:
	chroma_collection.delete(chroma_collection.get()["ids"])

chroma_collection.add(
	ids=ids,
	embeddings=embeddings,
	documents=chunks_list,
	metadatas=metadatas
)


#----------------------------------------
# Tools
#----------------------------------------
def send_notification(message: str):
	if pushover_user is None or pushover_token is None:
		return "Notification failed: Pushover is not configured"
	payload = {
		"token": pushover_token,
		"user": pushover_user,
		"message": message
	}
	requests.post(pushover_url, data=payload)

def roll_dice():
	return random.randint(1, 6)

send_notification_function={
	"name": "send_notification",
	"description": "Send a push notification to Pushover account phone. Use this to alert important events or updates.", #tells the LLM what it is for
	"parameters": {
		"type": "object",
		"properties": {
			"message": {
				"type": "string",
				"description": "The message to send in the notification."
			}
		},
		"required": ["message"]
	}
}

def get_weather(location: str = "Blacksburg, VA"):
	# Geocode the location name to lat/lon
	geo_resp = requests.get(
		"https://geocoding-api.open-meteo.com/v1/search",
		params={"name": location, "count": 1}
	).json()

	if not geo_resp.get("results"):
		return f"Could not find location: {location}"

	lat = geo_resp["results"][0]["latitude"]
	lon = geo_resp["results"][0]["longitude"]

	weather_resp = requests.get(
		"https://api.open-meteo.com/v1/forecast",
		params={
			"latitude": lat,
			"longitude": lon,
			"current": "temperature_2m,weather_code,wind_speed_10m",
			"temperature_unit": "fahrenheit"
		}
	).json()

	current = weather_resp["current"]
	temp = current["temperature_2m"]
	wind = current["wind_speed_10m"]

	return f"Current weather in {location}: {temp}°F, wind {wind} mph."

roll_dice_function={
	"name": "roll_dice",
	"description": "Roll a six-sided dice and return the result. Use this to generate random numbers between 1 and 6.", #tells the LLM what it is for
	"parameters": {
		"type": "object",
		"properties": {}, # empty properties since no parameters are needed for rolling a dice
		"required": []
	}
}

get_weather_function={
	"name": "get_weather",
	"description": "Get the current weather for a location. Use this when asked about weather, temperature, or conditions where Joel lives.",
	"parameters": {
		"type": "object",
		"properties": {
			"location": {
				"type": "string",
				"description": "City and state, e.g. 'Blacksburg, VA'. Defaults to Joel's location if not specified."
			}
		},
		"required": []
	}
}

tools = [
	{"type":"function","function":send_notification_function},
	{"type":"function","function":roll_dice_function},
	{"type":"function","function":get_weather_function}
	]

def handle_tool_call(tool_calls):
	results_list = []

	for tool_call in tool_calls:
		function_name = tool_call.function.name
		args = json.loads(tool_call.function.arguments)
		#print(f"Function name: {function_name}, Arguments: {args}")
		if function_name == "send_notification":
			send_notification(args["message"])
			function_content = f"Notification sent with message: {args['message']}"
		elif function_name == "roll_dice":
			roll_result = roll_dice()
			function_content = f"Dice rolled: {roll_result}"
		elif function_name == "get_weather":
			location = args.get("location", "Blacksburg, VA")
			function_content = f"{get_weather(location)}"
		#	function_name_2(args)
		else:
			function_content = f"Unknown function: {function_name}"

		tool_call_result = {
			"role": "tool",
			"content": function_content,
			"tool_call_id": tool_call.id
		}
		results_list.append(tool_call_result)

	return results_list

#-----------------------------------
# System Message
#-----------------------------------
# this is not necessary but might be worht it
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
	# RAG 
	# embed the query using the same model ww used for the chunks to ensure compatability
	query_embedding = client.embeddings.create(
		input=[message],
		model="text-embedding-3-small"  # match whatever model you used for chunks
	).data[0].embedding

	#Search ChromaDB
	query_results = chroma_collection.query(
		query_embeddings=[query_embedding],
		n_results=5,
		include=["documents", "metadatas", "distances"] # documents and metadatas are the defualt
	)

	# create enhanced system message with chunks content
	context = "\n---\n".join(query_results["documents"][0])


	system_message_enhanced = system_message + "\n\nContect:\n" + context

	# as usual
	message_to_llm = [{"role": "system", "content": system_message_enhanced}] + history + [{"role": "user", "content": message}]

	llm_response = client.chat.completions.create(
		model="gpt-4.1-mini",
		messages=message_to_llm,
		tools=tools
	)

	llm_message = llm_response.choices[0].message

	# check if AI wants to call a tool
	while llm_message.tool_calls:
		# handle tool call
		tool_call_response = handle_tool_call(llm_message.tool_calls) # list of tool calls, but we only have one for now
		# add info about tool call respose to "context"
		message_to_llm.append(llm_message)
		for response in tool_call_response:
			message_to_llm.append(response)
		# message_to_llm.extend(tool_call_response) this works too but I like the loop for clarity
		# invoke the LLM one more time to get it's updated response
		llm_response = client.chat.completions.create(
			model="gpt-4.1-mini",
			messages=message_to_llm,
			tools=tools 
		)
		llm_message = llm_response.choices[0].message

		# add protection to avoid infinite loops
		if len(message_to_llm) > 10:  # arbitrary limit to prevent infinite loops
			break

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























