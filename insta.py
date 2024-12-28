import os
import random
from pathlib import Path
from instagrapi import Client
from time import sleep
import ollama

class InstagramAutomation:
    def __init__(self, username, password, image_directory='.'):
        self.username = username
        self.password = password
        self.image_directory = Path(image_directory)
        self.uploaded_file = self.image_directory / 'uploaded_images.txt'
        self.client = Client()
        self.ollama_client = ollama.Client(host="http://localhost:11434")
        self.model_name = 'llama3.2-vision'

    def login(self):
        """Log in to Instagram account"""
        try:
            self.client.login(self.username, self.password)
            print("Successfully logged in to Instagram")
            return True
        except Exception as e:
            print(f"Failed to login to Instagram: {e}")
            return False

    def load_uploaded_images(self):
        """Load the list of previously uploaded images"""
        if not self.uploaded_file.exists():
            print("Creating new uploaded images tracking file")
            return set()
        try:
            with open(self.uploaded_file, 'r') as f:
                uploaded = set(f.read().splitlines())
            print(f"Loaded {len(uploaded)} previously uploaded images")
            return uploaded
        except Exception as e:
            print(f"Error loading uploaded images: {e}")
            return set()

    def save_uploaded_image(self, image_path):
        """Record an uploaded image"""
        try:
            with open(self.uploaded_file, 'a') as f:
                f.write(f"{image_path}\n")
            print(f"Recorded uploaded image: {image_path}")
        except Exception as e:
            print(f"Failed to record uploaded image: {e}")

    def select_images(self, uploaded_images, num_images=5):
        """Select random unuploaded images"""
        image_extensions = {'.png', '.jpg', '.jpeg'}
        all_images = [
            str(f) for f in self.image_directory.iterdir()
            if f.suffix.lower() in image_extensions
        ]
        available_images = [img for img in all_images if img not in uploaded_images]
        print(f"Found {len(all_images)} total images, {len(available_images)} available")
        if not available_images:
            return []
        selected = random.sample(available_images, min(num_images, len(available_images)))
        print(f"Selected for upload: {selected}")
        return selected

    def generate_caption(self, image_path):
        """Generate image caption using llama3.2-vision model"""
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[{
                    'role': 'user',
                    'content': 'Describe what is in this image without starting with "The image shows", start immediately with description.',
                    'images': [image_path]
                }]
            )
            # Extract the content from the response
            caption_content = response.message.content.strip()
            if caption_content:
                caption = caption_content + "\n\n✨ AI-generated images"
            else:
                caption = "✨ AI-generated pajama piece ✨\n\n#AIArt #DigitalArt"
            print(f"Generated caption for {image_path}: {caption}")
            return caption
        except Exception as e:
            print(f"Caption generation failed: {e}")
            return "✨ AI-generated pajama piece ✨\n\n#AIArt #DigitalArt"

    def upload_images(self, image_paths):
        """Upload images to Instagram"""
        for image_path in image_paths:
            try:
                print(f"Generating caption for {image_path}")
                caption = self.generate_caption(image_path)
                print(f"Uploading {image_path} with caption: {caption[:100]}...")
                self.client.photo_upload(image_path, caption=caption)
                self.save_uploaded_image(image_path)
                print(f"Successfully uploaded: {image_path}")
                # Wait between uploads to avoid rate limiting
                sleep(random.uniform(30, 60))
            except Exception as e:
                print(f"Failed to upload {image_path}: {e}")
                continue

def main():
    # Configuration
    INSTAGRAM_USERNAME = 'your usename'
    INSTAGRAM_PASSWORD = 'your_password'
    IMAGE_DIRECTORY = '.'  # Replace with your image directory path
    # Initialize automation
    bot = InstagramAutomation(
        username=INSTAGRAM_USERNAME,
        password=INSTAGRAM_PASSWORD,
        image_directory=IMAGE_DIRECTORY
    )
    print("Starting Instagram automation...")
    if not bot.login():
        print("Login failed. Exiting...")
        return
    uploaded_images = bot.load_uploaded_images()
    image_paths = bot.select_images(uploaded_images)
    if not image_paths:
        print("No images available for upload. Exiting...")
        return
    bot.upload_images(image_paths)
    print("Upload session completed")

if __name__ == "__main__":
    main()