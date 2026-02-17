print("Om Gan Ganpataye Namaha !!")
import gradio as gr
from agent import get_agent_response

def create_gradio_interface():
	with gr.Blocks() as demo:
		gr.Image("SaraswatiMaa.avif", width=150, show_label=False)
		gr.Markdown("<h2 style='text-align: center;'>Ask Me Anything !!</h2>")

		history_textbox = gr.Chatbot(
			elem_id="chatbot",
			label="Chat",
			#placeholder="History Text Box",
			show_label=False,
			height=500,
			scale=1,
			type='messages'
		)
		msg_textbox = gr.Textbox(
			label="Message",
			placeholder="Message Text Box",
			show_label=False,
			container=False,
			scale=7

		)
		css = """
		#chatbot {
			height: 500px;
		}
		.gradio-container {
			max-width: 900px;
			margin: auto;
		}
		"""
		demo.css = css

		with gr.Row():
			submit_btn = gr.Button("Send", variant="primary", scale=1)
			clear_btn = gr.ClearButton(value="Clear Chat", scale=1)
			#gr.ClearButton(components=[msg_textbox], value="Clear Chat", scale=1)

		def user_submit_btn_click(input_message, history_message):
			print("Clicked Submit Button")
			if not input_message:
				return "", history_message
			history = history_message + [{"role":"user","content":input_message}]
			return "", history

		def user_clear_btn_click():
			print("Clicked Clear Button")
			return ""

		async def call_agent(history_message):
			#print("history_message:",history_message)
			#print("################################")
			#print("history_message[-1]:",history_message[-1])
			# #if history_message[-1]["role"] == "user":
				#print(history_message)

			last_user_message, full_chat_history = history_message[-1]["content"],history_message[:-1]
			print("################################")
			print("last_user_message:", last_user_message)
			print("full_chat_history:", full_chat_history)
			response = await get_agent_response(last_user_message,full_chat_history)
			history_message.append({"role":"assistant","content":response})
			return history_message


		#submit_btn.click(user_submit_btn_click,[msg_textbox, history_textbox],[msg_textbox, history_textbox])
		submit_btn.click(user_submit_btn_click, [msg_textbox, history_textbox], [msg_textbox, history_textbox]).then(call_agent,history_textbox, history_textbox)
		clear_btn.click(user_clear_btn_click,[],[msg_textbox])



	return demo

if __name__ == "__main__":
	app = create_gradio_interface()
	app.launch(
		server_name="0.0.0.0",
		server_port=8080,
		share=False,
	)

