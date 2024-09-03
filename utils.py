# Import the necessary libraries
import json
import tempfile
import os
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task
import re
from dotenv import load_dotenv


load_dotenv()

# Get the API Key from the Dashboard - https://playground.twelvelabs.io/dashboard/api-key
API_KEY = os.getenv("API_KEY")

# Create the INDEX ID as specified in the README.md and get the INDEX_ID
INDEX_ID = os.getenv("INDEX_ID")

# Initialize the Twelve Labs client
client = TwelveLabs(api_key=API_KEY)

# Create a temporary directory for uploaded files
UPLOAD_DIR = tempfile.mkdtemp()

def create_task(file_path):

    # Create a new task for video indexing
    return client.task.create(
        index_id=INDEX_ID,
        file=file_path,
    )

def on_task_update(task: Task):
    # Callback function to print task status updates
    print(f" Status={task.status}")

def wait_for_task(task):

    # Wait for the indexing task to complete
    task.wait_for_done(sleep_interval=5, callback=on_task_update)
    if task.status != "ready":
        raise RuntimeError(f"Indexing failed with status {task.status}")
    return task.video_id

def generate_mcq(video_id):
    # Prompt to generate the multiple choice questions based on video content
    prompt = """You're Educational Content Analyzer, and you are tasked to prepare 
    the three Multiple Choice Questions based on the video content and the 
    concept which is been discussed by the speaker or shown. The difficulty of 
    the question should also gradually increase. The response should be in the 
    json format where there is Q1, Q2, and Q3. Each section would contain 
    the question with options in question and the correct_answer"""
    

    # Twelve Labs SDK to generate text based on the video content
    gist_r = client.generate.text(
        video_id=video_id,
        prompt=prompt
    )
    return gist_r.data

def parse_json_with_regex(text):

    # Extract and parse JSON content from the response
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:

            # Return None if JSON parsing fails
            return None
    else:
        # Return None if no JSON like content is found
        return None

def save_uploaded_file(uploaded_file):

    # Save the uploaded file to the temporary directory
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


# Calculate the user's score based on their answers
def calculate_score(user_answers, questions):
    return sum(answer == questions[q_num]["correct_answer"] for q_num, answer in user_answers.items())