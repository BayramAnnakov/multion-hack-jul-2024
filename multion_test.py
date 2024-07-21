import dotenv

dotenv.load_dotenv()

import os

from multion.client import MultiOn

from mem0 import Memory

config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 6333,
                }
            },
        }

m = Memory.from_config(config)

client = MultiOn(
    api_key=os.getenv("MULTION_API_KEY")
)


client.browse(
    cmd = "Add Intelligent Investor book to the Amazon cart",
    url = "https://www.amazon.com/",
    local=True
)

# retrieveResponse = client.retrieve(
#     cmd="Get Bayram's Top Skills from LinkedIn",
#     url="https://www.linkedin.com/in/bayramannakov/",
#     fields=["skill"],
#     local=True

# )

# print(retrieveResponse)

# for item in retrieveResponse.data:
#     m.add(item["skill"], user_id="Bayram", metadata={"category": "skills"})


# skills = m.search(query="Bayram's Top Skills", user_id="Bayram")
