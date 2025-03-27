import json
import os
import time
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image
import base64
import os
# Fetch API key from GEMINI_API_KEY environment variable
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize the client, passing the API key explicitly
client = genai.Client(api_key=api_key)
import re  # Import the regular expression library

# Define base image directory and subdirectory
BASE_IMAGE_DIR = "../library_manager/static/images" # Corrected BASE_IMAGE_DIR for script location in utils
IMAGE_SUBDIR = "covers"  # You can change this if needed, or keep it empty string if no subdirectory is needed

image_folder = os.path.join(BASE_IMAGE_DIR, IMAGE_SUBDIR)  # Define folder to save images
os.makedirs(image_folder, exist_ok=True)  # Create folder if it doesn't exist


# --- New function to sanitize filename ---
def sanitize_filename(filename, max_length=50):
    """
    Sanitizes a filename by removing disallowed characters, replacing spaces with underscores,
    and truncating it to a maximum length.

    Args:
        filename (str): The filename to sanitize.
        max_length (int): The maximum length of the filename.

    Returns:
        str: The sanitized filename.
    """
    # Remove characters that are not alphanumeric, underscores, or hyphens
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '', filename)
    # Replace spaces with underscores (although spaces should already be removed by the regex above)
    sanitized_name = sanitized_name.replace(" ", "_")
    # Truncate filename if it's too long
    sanitized_name = sanitized_name[:max_length].rstrip('_') # remove trailing underscores after truncation
    return sanitized_name


def create_image_prompt(title, author):
    """
    Generates an image prompt for a book cover based on the title and author.

    Args:
        title (str): The title of the book.
        author (str): The author of the book.

    Returns:
        str: The generated image prompt.
    """
    prompt = f"Create a book cover for a book titled '{title}' by {author}."
    prompt += " The cover should be visually appealing and relevant to the book's title, it should have something stereotypical on its cover, it can be funny."
    return prompt

def save_image(image_data, filename):
    """
    Saves image data to a file.

    Args:
        image_data (bytes): The raw image data.
        filename (str): The filename to save the image as.
    """
    image = Image.open(BytesIO(image_data))
    image.save(filename)
    print(f"Image saved as '{filename}'")


def load_books_data(filepath="library_manager\\backend\\books_data.json"):
    """Loads book data from a JSON file."""
    try:
        with open(filepath, "r") as f:
            books_data = json.load(f)
        return books_data
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return []
    except json.JSONDecodeError:
        print(
            f"Error: Could not decode JSON from {filepath}. Is the file properly formatted?"
        )
        return []


def save_books_data(books_data, filepath="library_manager\\backend\\books_data.json"):
    """Saves book data to a JSON file."""
    try:
        with open(filepath, "w") as f:
            json.dump(books_data, f, indent=4)
        print(f"Book data saved to '{filepath}'")
    except Exception as e:
        print(f"Error saving book data to '{filepath}': {e}")



books_data = load_books_data()  # Load book data from JSON

if not books_data:  # Check if books_data is empty
    print("No book data loaded. Exiting.")
else:
    for book in books_data:
            if 'library_seal' in book["image"]: # Check if library_seal key exists
                title = book["title"]
                author = book["author"]
                prompt = create_image_prompt(title, author)

                print(f"Generating image for '{title}'...")  # Indicate image generation start

                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp-image-generation",
                    contents=prompt,
                    config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
                )

                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:  # Check if part is image data
                        image_data = part.inline_data.data
                        # --- Modified filename generation ---
                        sanitized_title = sanitize_filename(title)
                        filename = os.path.join(image_folder, f"{sanitized_title}_cover.jpg") # Using os.path.join and .jpg extension
                        save_image(image_data, filename)
                        json_filename = filename.replace("\\", "/") # Replace backslashes with forward slashes for JSON
                        book["image"] = json_filename  # Update books_data with the image filename in JSON format
                        print(f"Updated book data for '{title}' with image filename.")  # Confirmation message
                        save_books_data(books_data)  # Save books_data after each image update
                    elif part.text is not None:
                        print(f"Text response for '{title}': {part.text}")  # Print text response if any
                time.sleep(20)
            else:
                print(f"Skipping image generation for '{book['title']}' as it does not have 'library_seal'.")

    print("\nImage generation and saving process completed.")  # Final completion message
    print("Updated books_data saved to books_data.json")
