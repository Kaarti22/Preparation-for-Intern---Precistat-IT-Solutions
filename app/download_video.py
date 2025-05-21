import requests

url = "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"
response = requests.get(url, verify=False)

with open("test_video.mp4", "wb") as f:
    f.write(response.content)

print("Downloaded sample_640x360.mp4 as test_video.mp4")
