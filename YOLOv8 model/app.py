import streamlit as st
from PIL import Image
import os
from ultralytics import YOLO
import uuid

st.title("🦷 Dental X-ray Detection with YOLOv8")

uploaded_file = st.file_uploader("Upload a dental X-ray image", type=["jpg", "jpeg", "png"])

@st.cache_resource
def load_model():
    return YOLO("best (1).pt")

model = load_model()

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Detecting..."):
        results = model.predict(source=temp_filename, save=True, conf=0.3)

    result_dir = results[0].save_dir
    pred_image_path = os.path.join(result_dir, os.path.basename(temp_filename))

    st.image(pred_image_path, caption="Detected Image", use_container_width=True)

    with open(pred_image_path, "rb") as img_file:
        st.download_button("📥 Download Result", img_file, file_name="dental_detected.jpg", mime="image/jpeg")

    os.remove(temp_filename)
