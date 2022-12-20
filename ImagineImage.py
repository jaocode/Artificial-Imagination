import openai   # Provides access to OpenAI's RESTful API's
import os.path  # For working with files
import requests # Required to download generated pictures
from datetime import datetime # Used for filename timestamps

# Location to store the output picture and html files.
output_path = './output'

# Reads the API key from the openai.key file and provides it to OpenAI API
# This is required for accessing GPT-3 and DALL-E.
# Get a key by creating an account at openai.com 
def init_openai():
    # API_KEY is associated with your account and should be kept secret
    with open('./openai.key', 'r') as k:
        print ('here')
        key = k.readline()
        openai.api_key = key
        k.close

# Queries openai DALL-E to generate a picture for the given prompt.
def query_DALLE(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
        )
    image_url = response['data'][0]['url']

    return image_url

#Queries OpenAI's GPT-3 for an image description.
def query_GPT3 ():    
    start_sequence = "\nResponse: "
    restart_sequence = "\nPrompt: "
    
    #The GPT-3 davinci-003 differs from davinci-002 by providing much more elaborate descriptions that
    #are two big for use as prompts for image generators. 
    prompt = "Prompt: Imagine a picture and give a two sentence description of it."

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Prompt:", " Response:"]
        )

    result = response.choices[0].text

    prompt += start_sequence + result

    result = result.replace('Response:', '')

    return result

def gen_filename ():
    # Getting the current date and time
    dt = datetime.now()

    # Getting a timestamp for use as the filename. This prevents name collisions.
    result = int(datetime.timestamp(dt))

    return result

def download_picture (url, filename):
    response = requests.get(url)
    if os.path.exists (output_path) == False:
        os.mkdir('{0}'.format(output_path))
    os.mkdir('{0}/{1}'.format(output_path, filename))
    open('{0}/{1}/picture.png'.format(output_path, filename), 'wb').write(response.content)

if __name__ == '__main__':
    init_openai()

    # Query GPT-3 for a picture description.
    resp = query_GPT3()
    print ("Response: " + resp)

    # Query DALL-E to create a picture using the description
    url = query_DALLE(resp)

    # Download the generated picture
    filename = gen_filename ()
    download_picture(url, filename)
    
    # Create a html file with description prompt and picture
    with open('{0}/{1}/{1}.html'.format(output_path, filename), 'w') as f:
        f.write('<!DOCTYPE html>')
        f.write('<html><body>')
        f.write('<h1>Generated Description</h1>')
        f.write('<p>{0}</p>'.format(resp))
        f.write('<h1>Generated Image</h1>')
        f.write('<img src="picture.png">')
        f.write('</body></html>')
        f.close()

    # Print the directory containing the generated picture to the console.
    print ("Image location: {0}/{1}".format(output_path, filename))

    print ('Done.')