import gradio as gr


gr.Interface(
  createMask, gr.inputs.Image(shape=(126, 126)), "image").launch()