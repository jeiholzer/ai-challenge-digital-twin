import os 
from openai import OpenAI
import gradio as gr
import chromadb
import re
import uuid
import random
import json
import requests
from pprint import pprint

#------------------------------------
#   SETUP
#------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
	raise Exception("OPENAI_API_KEY environment variable is not set.")
else:
	print(OPENAI_API_KEY[:8] + "..." + OPENAI_API_KEY[-8:], flush=True)  # Print first and last 8 characters of the API key for verification

client = OpenAI()

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")

if PUSHOVER_TOKEN:
	print(f"PUSHOVER_TOKEN loaded: {PUSHOVER_TOKEN[:6]}...", flush=True)
else:
	raise Exception("PUSHOVER_TOKEN environment variable is not set.")

if PUSHOVER_USER:
	print(f"PUSHOVER_USER loaded: {PUSHOVER_USER[:6]}...", flush=True)
else:
	print("PUSHOVER_USER is None or missing!", flush=True)

#-----------------------------------
# Load a document
#-----------------------------------
document_overview = """
My name is Joel Eiholzer
I live in southwestern Virginia, USA. I am a software engineer with a passion for AI and machine learning. I enjoy learning new technologies and applying them to solve real-world problems.
20+ years of experience as a Project Manager and Software Developer, managing IT projects with an eye towards continuous process improvement. Project leadership of cross-functional remote teams, fostering team coordination through a culture of inclusion, prioritizing collaboration both within my team and outside the team. Eﬀective at collaborating with diverse personalities
I have run several marathons and triathlons. One day, I decided I wanted to be able to say I had run a marathon, so I made a plan and ran my first marathon in Columbus, Ohio. After a while, I got tired of just running, so I decided to try a triathlon. My first triathlon was at Clemson University in South Carolina. I have since run many marathons and several triathlons.
"""

document_education = """
I graduated from Jamesville-Dewitt High School, located in Dewitt, New York. While there, I was in the theater and choir, and a select singing group called the Roaring 20s. I also started my first job at their photocopy shop and videotaping sporting events.
I then attended SUNY Canton in Canton, New York, where I received an Associate Degree in Engineering Science. While there, I worked in the dining hall as a student manager.
I then moved on to Virginia Tech in Blacksburg, Virginia, where I received my Bachelor of Science in Computer Engineering. Initially, I studied Electrical Engineering but found I did not enjoy learning to generate electricity, engineer communications systems, or design digital circuits.  Switching to Computer Engineering kept me close to that and was far more interesting to me.
While at Virginia Tech, I joined the Phi Kappa Psi fraternity, where I served as President, Treasurer, and Chaplain.
"""

document_profesional_experience = """
Independent Contractor	07/2025 - Present
During this time, I have been working on several projects to continue developing my skills and learning.
Key Accomplishments
•	Site redesign and improvement for the property rental website brac.com using AI assistance.
•	Site redesign and improvement for the property rental website cbsrentals.com using AI assistance.
•	Various modifications and improvements to the furniture site bassettmirror.com, including requirements gathering and database development.
•	Achieved a PMI PMP certification
•	Achieved the AWS Certified AI Practitioner certification
•	Completed the AI Challenge, a six-week course on AI, complete with creating a digital twin
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

document_certifications = """
Certifications
SSGI Agile Professional (SSGI-CAP) -  certification is a basic introduction to agile practices for managers.
SAFe 6 Scrum Master (SSM) certification is a credential from Scaled Agile for people who serve as Scrum Masters on Agile teams within large organizations using the Scaled Agile Framework (SAFe). It validates more than basic Scrum knowledge: it focuses on helping a team work effectively within a larger, coordinated Agile delivery structure.
AWS Certified AI Practitioner validates in-demand knowledge of artificial intelligence (AI), machine learning (ML), and generative AI concepts and use cases. Sharpen your competitive edge and position yourself for career growth and higher earnings. I found this to be a great introductory overview of AI that was not easy but not very hard either.
The PMI Project Management Professional certification. - Demonstrate the ability to lead projects in any industry with this globally recognized certification and open the door to a world of opportunities. The Project Management Professional certification recognizes candidates skilled in managing the people, processes, and business priorities of professional projects. This was one of the hardest certifications I have ever gotten. Not so much because of the processes as because of the agile situational questions.
PMI Certified Professional in Managing AI (PMI-CPMAI) - gain the tools to build with AI effectively, giving you the playbook to secure AI success. In progress with expected certification in September 2026
Courses
AI Engineering Challenge – A great introduction to interacting with AI LLMs and creating a digital twin. I really enjoyed this experience.
PMI Generative AI Overview - Gives a basic understanding of Generative AI (GenAI) in project management. Explores different tools and their applications for enhanced project outcomes. This was a good high-level overview.
Clearances
Held Defense Industrial Security Clearance Office (DISCO)-issued Personnel Clearance Level (PCL) of Secret
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
document_projects = """
Project Management
Project Manager, HUD Exchange, U.S. Department of Housing and Urban Development - In 2019, I transitioned from a developer to Project Manager for the IT portion of the Community Compass contract. As a Project Manager, I was responsible for overseeing the maintenance tasks, functionality updates, and new development for portions of the HUD Exchange website. This work included resourcing the team and monitoring the IT budget.  I was also responsible for the website's quality assurance to ensure it met Client expectations. I helped ensure that HUD Exchange follows the ICF Project Management Framework as part of the Project Life Cycle that adheres to Capability Maturity Model Integration (CMMI) Level 3 practices. 
Project Manager, Internet Databases - I was responsible for project management across several projects. This included creating estimates for potential customers, gathering requirements, overseeing prototype design, guiding development efforts, and obtaining customer approval before releasing to production. The company’s main focus is on supporting furniture manufacturers with public and intranet websites.
Project Manager, Acquisition Information Management (AIM), US Army Acquisition, Logistics, and Technology Enterprise Systems and Services (ALTESS). - While employed at Automation Creations Inc. I worked as a project leader on the AIM project. This suite of applications gathers acquisition program information from the project managers and reports it up the chain to the U.S. Army leadership and the Office of the Secretary of Defense. He oversaw all aspects of the project life cycle, including maintaining cost, schedule, and performance information. I traveled to conferences to present information on the applications, instruct users in hands-on sessions, and gather feedback and requirements.
Web Development
Developer, HUD Exchange, U.S. Department of Housing and Urban Development (HUD) - As a web developer, I was responsible for several components of the HUDX Exchange website. One of the larger accomplishments was creating a new Training and Events app that included pulling data from an external Learning Management System via its API. I also added major modifications to the Ask A Question application. Technologies used were CFML, JavaScript, SVN, MURA CMS, and MS SQL Server.
Developer Cross-Site Evaluation OneNet System, U.S. Department of Justice - The OneNet system will replaced the TATIS-1 system recording on-site Training and Technical Assistance (T/TA) service delivery to States/Tribes. My responsibilities included database design and implementation, system architecture design, and application development. The technologies used are CFML, JavaScript, Model-Glue, SVN, and MS SQL Server.
Developer, Child Welfare Information Gateway Website (CWIG), Children’s Bureau Clearinghouse Services, Administration for Children and Families, U.S. Department of Health and Human Services - CWIG provided access to information and resources to help protect children and strengthen families. My responsibilities included helping maintain and update the site, including code and database changes. I assisted in a 9,000+ page redesign . 9,000+ page. My responsibilities included coding new web pages from content provided by the project manager. I rewrote the survey module including recoding the input, output and redesigning the database that holds the data. The technologies used were Payflow, Google Custom Search Engine, Model-Glue, Fusebox, ColdSpring, CFML, JavaScript, CSS, SVN, RSS, Verity Search, BASIS, MS SQL Server and Oracle.
Developer, IMS: Information Management System: Child Welfare, U.S. Department of Health and Human Services. This project involved building a backend management tool for the Child Welfare inventory management employees. The user interface design dictated the need for a rich internet application (RIA). My responsibility was to help create a highly functional prototype to support the development process. He is also working on modifying the current Childwelfare site to use the new database for displaying information. He aided in maintaining, tracking, and releasing database changes. The technologies used are Flex, Flash, MXML, Cairngorm, Cold Fusion 8, SVN, Model-Glue, and MS SQL Server.
Developer, National Responsible Fatherhood Clearinghouse, U.S. Dept. of Health and Human Services, Administration for Children and Families, Office of Family Assistance - The National Responsible Fatherhood Clearinghouse (NRFC) serves as a national repository and distribution center for information and research relating to responsible fatherhood programs, initiatives, and activities for professionals and individuals. My responsibilities included helping maintain and update the site. The technologies used Model-Glue, ColdSpring, Transfer, CFML, CSS, RSS, SVN, and Oracle.
Developer, National Healthy Marriage Resource Center, U.S. Department of Health and Human Services, Administration for Children and Families, Office of Family Assistance - The National Healthy Marriage Resource Center (NHMRC) provides group-based technical assistance to healthy marriage programs nationwide. My responsibilities included helping maintain and update the site. The technologies used Model-Glue, ColdSpring, Transfer, Farcry, CFML, CSS, RSS, SVN, MySQL, MS SQL Server, and Oracle.
Developer, Welfare Peer Technical Assistance Network (PeerTA) Office of Family Assistance, Administration for Children and Families, U.S. Department of Health and Human Services - Welfare Peer TA provides peer-to-peer technical assistance to public agencies and private organizations operating the Temporary Assistance for Needy Families (TANF) program. My responsibilities included helping maintain and update the site. As part of this effort, I worked to import data from an Access database into MS SQL by writing SQL Scripts and modifying existing pages to use the new database design. The technologies used Model-Glue, ColdSpring, Transfer, CFML, CSS, RSS, SVN, and MS SQL Server.
Developer, Air Force Community Assessments Results (AFCAR), U.S. Air Force - This project involved displaying the results of a mental survey for all Air Force bases. My responsibilities were to create a Fusebox framework for developers to work from and to research possibilities for generating various graphs to display the information. I worked directly with the site designer to help ensure all functionality was present. He worked directly with the database designer to ensure the table design would support the coding. I also assisted with the production and review of CMMI documentation to achieve CMMI Level 2 certification. The technologies used were Cold Fusion, Fusebox, DHTML, CSS and MS SQL Server.
Developer - National Training and Technical Assistance Center (NTTAC), U.S. Department of Justice -  National Training and Technical Assistance Center (NTTAC) delivers, brokers, and promotes the highest quality training and technical assistance to the juvenile justice field and its related criminal justice initiatives by utilizing a vast array of training and technical assistance resources funded through the Office of Juvenile Justice and Delinquency Prevention (OJJDP) and its partners. My responsibilities included maintaining the site, coding a complete redesign of the site, merging a second website into this site, and consulting with others to make database changes and general additions as the site grows. The technologies used are Cold Fusion, Mach-II, MetaMIS, JSP, DHTML, CSS, SVN, and MS SQL Server.
Developer - Training and Technical Assistance Center (TTAC), U.S. Department of Justice - This project focused on creating a learning community to strengthen the capacity of victim assistance organizations across the country. My responsibilities were mainly maintaining the site, including modifications and updates. I aided in a complete redesign by helping recode pages. The technologies used were Cold Fusion, Fusebox, DHTML, CSS, and MS SQL Server.
Developer, Louisiana Road Home: Homeowner Application Data Entry, State of Louisiana -  This project involved creating a series of forms to enter data from handwritten applications. My responsibilities were to use the Fusebox framework to code much of the form logic and validate that the information entered was in acceptable formats. The technologies used were Cold Fusion, Fusebox, QForms, and MS SQL.
Developer, Piedmont Arts – The website supports an award-winning art museum that curates thought-provoking exhibitions by international, national, and regional artists. The museum also offers performing arts, from concerts to plays to children's performances, and art classes for all ages. I was asked to implement a payment system using Clover Payment Processing. The implementation involved API calls and webhooks using ColdFusion and JavaScript.
Developer, My Furnishweb - This is a portal supporting multiple furniture companies, where dealers and reps can access detailed information on orders, invoices, products, sales, etc. It involves integrating data from multiple sources and transforming it into a common database structure shared by all manufacturers. We also support custom forms associated with this site. I help maintain and add requested functionality. Technologies used were Lucee, CFML, python, jQuery, Bootstrap, AJAX calls, APIs, and MySQL.
Project Manager/Developer
Project Manager/Developer, Bassett Mirror Company - This is a site for a furniture manufacturer displaying their products. It also allows registered buyers to log in and order products through an online cart. I work directly with the customer to gather requirements, give estimates, and meet bi-weekly for updates. I also support backend development, adding new functionality primarily related to site and user administration. I reworked the data import from Excel spreadsheets into the database. Technologies used Lucee and MySQL.
Project Manager/Developer, Dynamic Resume Entry Site, River Marine Management - While employed at Internet Databases, I was responsible for gathering requirements, designing the database, coding, and testing. The site allows applicants to apply for jobs with the company online and to print a PDF of the entered information. The information is saved in a database for later retrieval by the Human Resources staff. The technologies used for this site were Cold Fusion, Java, and MySQL.
Project Manager/Developer, Online Invoicing System, River Marine Management - While employed at Internet Databases, I was responsible for requirements gathering, site design, and concept exploration. This site was designed to allow River Marine Management to access invoice information from various locations over the internet. The technologies used for this site were Cold Fusion, MySql and the database in Smartware.
Project Manager/Developer, Harvey Plexico – I worked directly with the client to gather requirements and provide estimates. I designed coded the site. Technologies used were HTML Bootstrap, and JavaScript.
"""

#-----------------------------------
# Chunking function 
#-----------------------------------
def chunk_text(text, max_chars=400, min_chars=300, overlap=50):
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
	{"text": document_certifications, "source": "Certifications and courses"},
	{"text": document_technical_skills, "source": "Technical Skills and Proficiencies"},
	{"text": document_projects, "source": "Projects that I have worked on"}
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
	if PUSHOVER_USER is None or PUSHOVER_TOKEN is None:
		return "Notification failed: Pushover is not configured"
	payload = {
		"token": PUSHOVER_TOKEN,
		"user": PUSHOVER_USER,
		"message": message
	}
	requests.post(PUSHOVER_URL, data=payload)

def roll_dice():
	return random.randint(1, 6)

def get_weather(location: str = "Christiansburg, VA"):
	headers = {"User-Agent": "JoelsDigitalTwin (joel@example.com)"}

	# Step 1: Geocode the location name to lat/lon (still using Open-Meteo's free geocoder for this part)
	geo_response = requests.get(
		"https://geocoding-api.open-meteo.com/v1/search",
		params={"name": location, "count": 1}
	)
	geo_resp = geo_response.json()

	print(f"Geocoding API status: {geo_response.status_code}", flush=True)
	print(f"Geocoding API response: {geo_resp}", flush=True)

	if not geo_resp.get("results"):
		return f"Could not find location: {location}"

	lat = geo_resp["results"][0]["latitude"]
	lon = geo_resp["results"][0]["longitude"]

	# Step 2: Get the NWS grid point for these coordinates
	points_response = requests.get(
		f"https://api.weather.gov/points/{lat},{lon}",
		headers=headers
	)
	points_resp = points_response.json()

	print(f"NWS points API status: {points_response.status_code}", flush=True)
	print(f"NWS points API response: {points_resp}", flush=True)

	if "properties" not in points_resp:
		error_reason = points_resp.get("detail", "Unknown error from NWS points API")
		return f"NWS lookup failed for {location}: {error_reason}"

	forecast_url = points_resp["properties"]["forecast"]

	# Step 3: Get the actual forecast
	forecast_response = requests.get(forecast_url, headers=headers)
	forecast_resp = forecast_response.json()

	print(f"NWS forecast API status: {forecast_response.status_code}", flush=True)
	print(f"NWS forecast API response: {forecast_resp}", flush=True)

	if "properties" not in forecast_resp:
		error_reason = forecast_resp.get("detail", "Unknown error from NWS forecast API")
		return f"Forecast fetch failed for {location}: {error_reason}"

	periods = forecast_resp["properties"].get("periods")
	if not periods:
		return f"No forecast periods returned for {location}"

	current_period = periods[0]
	name = current_period["name"]
	temp = current_period["temperature"]
	unit = current_period["temperatureUnit"]
	forecast_text = current_period["detailedForecast"]

	result = f"{name} in {location}: {temp}°{unit}. {forecast_text}"
	print(f"get_weather result: {result}", flush=True)

	return result

send_notification_function={
	"name": "send_notification",
	"description": "Send a push notification to Joel's phone. Only call this when the user explicitly wants something sent to Joel right now — either (1) \
		they've provided their contact information (name, email, phone) to be passed along, or (2) they directly ask you to message/tell/notify Joel something \
		specific (e.g. 'message Joel...', 'let Joel know...', 'tell him...'). Do NOT call this just because someone expresses general interest in contacting Joel \
		— wait for explicit contact details or an explicit message request.",
	"parameters": {
		"type": "object",
		"properties": {
			"message": {
				"type": "string",
				"description": "The content to send to Joel — either the contact info provided, or the specific message the user asked to be relayed."
			}
		},
		"required": ["message"]
	}
}

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
	"description": "Get the current weather for a location. If the user asks about the weather where Joel lives, or just asks about \
		'the weather' with no location given, call this with no 'location' argument (or leave it blank) so it defaults to \
		Christiansburg, VA. If the user asks about weather in a specific city, or names their own city and state, pass that \
		city and state as the 'location' argument instead.",
	"parameters": {
		"type": "object",
		"properties": {
			"location": {
				"type": "string",
				"description": "City and state, e.g. 'Roanoke, VA'. Omit this to default to Joel's location, Christiansburg, VA."
			}
		},
		"required": []
	}
}

tools = [{"type":"function","function":send_notification_function}]
tools.append({"type":"function","function":roll_dice_function})
tools.append({"type":"function","function":get_weather_function})

def handle_tool_call(tool_calls):
	results_list = []

	for tool_call in tool_calls:
		function_name = tool_call.function.name
		args = json.loads(tool_call.function.arguments)
		print(f"Function name: {function_name}, Arguments: {args}", flush=True)
		if function_name == "send_notification":
			send_notification(args["message"])
			function_content = f"Notification sent with message: {args['message']}"
		elif function_name == "roll_dice":
			roll_result = roll_dice()
			function_content = f"Dice rolled: {roll_result}"
		elif function_name == "get_weather":
			location = args.get("location", "Christiansburg, VA")
			function_content = f"{get_weather(location)}"
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
# this is not necessary but might be worth it
system_message = "You are a helpful assistant that answers questions based on the provided content. \
	If you don't know the answer, say that you don't know. Always use all available information to provide \
	the best answer. Important: do not talk about any topics that are not in the provided context. \
	And only use the information provided in the context to answer the question. If the question is not related \
	to the content, say you don't know. \
	Keep your answers somewhat concise. If they want more information on something, you tell them they can ask a follow-up question. \
	Only send Joel a notification in two cases: (1) the user has explicitly provided their contact information \
	(name, email, or phone) to be passed along, or (2) the user explicitly asks you to message, tell, or notify Joel \
	something specific. If someone merely expresses interest in contacting Joel without giving details, ask for their \
	contact information instead of sending a notification. Never send a notification just because someone seems \
	interested in reaching out."

#-----------------------------------
# Main Response function
#-----------------------------------
def response_ai(message,history):
	# RAG 
	# embed the query using the same model we used for the chunks to ensure compatibility
	query_embedding = client.embeddings.create(
		input=[message],
		model="text-embedding-3-small"  # match whatever model you used for chunks
	).data[0].embedding

	#Search ChromaDB
	query_results = chroma_collection.query(
		query_embeddings=[query_embedding],
		n_results=10,
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

	tool_call_count = 0
	max_tool_calls = 50

	# check if AI wants to call a tool
	while llm_message.tool_calls:
		tool_call_count += len(llm_message.tool_calls)  # count each individual tool call
		# handle tool call
		tool_call_response = handle_tool_call(llm_message.tool_calls) # list of tool calls, but we only have one for now
		# add info about tool call respose to "context"
		message_to_llm.append(llm_message)
		for response in tool_call_response:
			message_to_llm.append(response)
		# message_to_llm.extend(tool_call_response) this works too but I like the loop for clarity

		tool_call_count += 1
		if tool_call_count >= max_tool_calls:
			print(f"Tool call limit hit after {tool_call_count} calls", flush=True)
			return "Sorry, I got stuck trying to complete that request. Could you try rephrasing or asking something simpler?"
		
		# invoke the LLM one more time to get it's updated response
		llm_response = client.chat.completions.create(
			model="gpt-4.1-mini",
			messages=message_to_llm,
			tools=tools 
		)
		llm_message = llm_response.choices[0].message

	return(llm_message.content)

#-----------------------------------
# Launch Gradio
#-----------------------------------
gr.ChatInterface(
    fn=response_ai,
    title="Joel's first digital twin",
    chatbot=gr.Chatbot(
        avatar_images=(None, "head.jpg"),
        value=[{"role": "assistant", "content": "Hey, I'm Joel's digital twin — ask me anything about my background, projects, or skills! You can also contact me through here or just ask about the weather where I am or where you are."}]
    ),
    description="Chat with my twin to learn more about me",
	examples=["Tell me interesting facts about you","How can I contact you"]
).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

