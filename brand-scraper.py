import requests
from PIL import Image
import boto3
import io
import os
from dotenv import load_dotenv

# Load environment variables from a .env file in the same directory
load_dotenv()

# Function to read domains from a file
def read_domains(file_path):
    with open(file_path, 'r') as file:
        # Read each line, strip all leading/trailing whitespaces and newlines
        return [line.strip() for line in file if line.strip()]


# Function to download and convert .ico file to .png format
def download_and_convert_ico(domain):
    try:
        # Send a GET request to fetch the favicon.ico from the domain
        response = requests.get(f"https://{domain}/favicon.ico", stream=True)
        # Raise an error for bad status codes
        response.raise_for_status()
        return io.BytesIO(response.content)
        
        # Convert to PNG
        # image = Image.open(io.BytesIO(response.content))
        # output = io.BytesIO()
        # image.save(output, format='PNG')
        # Reset the buffer position to the beginning
        # output.seek(0)
        # return output

    except requests.RequestException as e:
        print(f"Failed to download .ico from {domain}: {e}")
        return None

# Function to upload a file to an S3 bucket
def upload_to_s3(bucket_name, file_obj, file_name):
    # Initialize the S3 client with credentials from env vars
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name = os.getenv("AWS_REGION")
    )

    full_file_path = f"public/favicons/{file_name}"

    # Upload the file object to the specified S3 bucket
    s3.upload_fileobj(file_obj, bucket_name, full_file_path)

# Function to save a file locally
def save_locally(file_obj, file_name):
    with open(file_name, 'wb') as file:
        # Write the contents of file_obj to a local file
        file.write(file_obj.read())

def main():
    S3_SWITCH = True

    domains = read_domains("websites.txt")
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
    local_directory = "local-test-icons-dir"

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    for domain in domains:
        print ("---")
        print("current website:")
        print (domain)
        print ("---")

        file_obj = download_and_convert_ico(domain)

        if file_obj:
            # file_name = f"{domain.split('.')[0]}-icon.png"
            file_name = f"{domain.split('.')[0]}-icon.ico"
            local_file_path = os.path.join(local_directory, file_name)

            if S3_SWITCH:
                # Upload the icon to the S3 bucket
                upload_to_s3(bucket_name, file_obj, file_name)
                print(f"Uploaded {file_name} to S3 bucket.")

            if S3_SWITCH == False:
                # Save the icons locally
                save_locally(file_obj, local_file_path)
                print(f"Saved {file_name} locally in {local_directory}")

if __name__ == "__main__":
    main()
