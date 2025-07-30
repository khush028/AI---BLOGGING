import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# === API Configurations ===
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
MODEL_NAME = "llama3-8b-8192"

# === Image Generation Function ===
def generate_image_from_stability(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json",
    }

    # Prepare the payload for multipart/form-data
    files = {
        "file": (None, prompt),  # Prompt is passed as a "file" for the request
    }

    data = {
        "model": "stable-diffusion-xl",
        "prompt": prompt,
        "output_format": "png",
        "steps": 30,
        "seed": 0, 
    }

    # Request image generation
    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        # Extracting the image from the response
        image_data = response.json()
        base64_image = image_data["image"]  # Base64 string of the generated image
        return base64_image
    else:
        raise Exception(f"Stability API error: {response.status_code} - {response.text}")
# === UI ===
st.title("✍🏻 🤖 BlogCraft: Your AI Writing Companion")
st.subheader("Now you can craft the perfect blog with the help of AI — BlogCraft is your new AI blog companion!")

with st.sidebar:
    st.title("Input Your Blog Details")
    blog_title = st.text_input("Enter Title")
    keywords = st.text_input("Keywords (comma-separated)")
    num_words = st.slider("Number of Words", min_value=250, max_value=1000, step=250)
    num_images = st.number_input("Number of Images", min_value=1, max_value=4, step=1)
    submit_button = st.button("Generate Blog")

# === On Button Click ===
if submit_button:
    if not blog_title or not keywords:
        st.error("Please enter both a blog title and keywords.")
    else:
        with st.spinner("Generating your blog..."):
            try:
                # === Blog Generation (Groq) ===
                prompt = (
                    f"Write a blog post titled '{blog_title}' using the following keywords: {keywords}. "
                    f"The blog should be approximately {num_words} words long. "
                    "Make it engaging and informative."
                )

                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }

                data = {
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant for writing blogs."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }

                response = requests.post(GROQ_API_URL, headers=headers, json=data)

                if response.status_code == 200:
                    blog_content = response.json()["choices"][0]["message"]["content"]
                    st.subheader("📝 Generated Blog")
                    st.write(blog_content)

                    # === Image Generation (Stability AI) ===
                    st.subheader("🎨 AI-Generated Images")
                    for i in range(num_images):
                        try:
                            image_prompt = f"{blog_title}, concept art, digital painting"
                            img_base64 = generate_image_from_stability(image_prompt)
                            img_bytes = base64.b64decode(img_base64)
                            img = Image.open(BytesIO(img_bytes))
                            st.image(img, caption=f"Image {i+1}: {image_prompt}", use_column_width=False)
                        except Exception as img_error:
                            st.warning(f"Image {i+1} failed to generate: {img_error}")
                else:
                    st.error(f"GROQ API Error: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"Something went wrong: {e}")
