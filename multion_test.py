import dotenv

dotenv.load_dotenv()

import os

from multion.client import MultiOn

client = MultiOn(
    api_key=os.getenv("MULTION_API_KEY")
)


retrieveResponse = client.retrieve(
    cmd="Get Bayram's Top Skills from LinkedIn",
    url="https://www.linkedin.com/in/bayramannakov/",
    fields=["skill"],
    local=True

)

print(retrieveResponse)