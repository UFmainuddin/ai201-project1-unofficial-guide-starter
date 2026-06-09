"""
Milestone 5: Gradio web UI for the Flushing Housing RAG system.
Run with: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from query import ask
from embed import get_model, get_collection


def handle_query(question):
    """Handle a user question and return answer + formatted sources."""
    if not question or not question.strip():
        return "Please enter a question.", ""

    result = ask(question.strip())
    answer = result["answer"]
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return answer, sources


# Pre-load model and vector store at startup so first query is fast
print("Loading embedding model and vector store...")
get_model()
get_collection()
print("Ready. Starting Gradio UI...")

with gr.Blocks(title="Flushing Off-Campus Housing Guide") as demo:
    gr.Markdown(
        "## The Unofficial Guide: Flushing Off-Campus Housing\n"
        "Ask questions about renting near Queens College in Flushing, Queens. "
        "Answers are grounded in collected documents — sources are shown below each answer."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g., How much is a one-bedroom apartment in Flushing?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=10)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Markdown(
        "**Sample questions to try:**\n"
        "- How much does a one-bedroom cost in Flushing?\n"
        "- How do I get from Queens College to Flushing by bus?\n"
        "- What are quieter neighborhoods near Flushing for students?\n"
        "- What do I do if my landlord won't fix the heat?\n"
        "- Where can I get cheap food near Flushing Main Street?"
    )


if __name__ == "__main__":
    demo.launch()
