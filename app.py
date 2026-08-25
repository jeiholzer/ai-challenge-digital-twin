import gradio as gr

def respond(message, history):
	response = f"You said: {message}\n\
		And I say what a beautiful day!"
	return response

gr.ChatInterface(
	fn=respond,
	title="Joel's first digital twin",
	chatbot=gr.Chatbot(),
	description="Chat with my twin on line"
).launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT",7860)))
