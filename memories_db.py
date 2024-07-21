import dotenv

dotenv.load_dotenv()

from multion.client import MultiOn
from mem0 import Memory

import os

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


#m.add("I've heard from my colleague Tim about Lex Fridman's talk with Bill Ackman and his controversial political views and invesments ", user_id="Bayram", metadata={"category": "daily memories"})
# m.add("Likes to watch Lex Fridman's podcasts", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to build & participate in hackathons", user_id="Bayram", metadata={"category": "interests"})
# m.add("Excited about AI & ML", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to read books about systems thinking", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to read books about psychology", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to read books about economics and investing", user_id="Bayram", metadata={"category": "interests"})

# memories = m.search(query="Bill Ackman talk with Lex Fridman", user_id="Bayram")

# print(memories)

def reset_memories(user_id: str):
    m.delete_all(user_id=user_id)

def populate_memories(user_id: str):
    m.add("I've heard from my colleague Tim about Lex Fridman's talk with Bill Ackman and his controversial political views and invesments ", user_id=user_id, metadata={"category": "daily memories"})
    m.add("Likes to watch Lex Fridman's podcasts", user_id=user_id, metadata={"category": "interests"})
    m.add("Likes to build & participate in hackathons", user_id=user_id, metadata={"category": "interests"})
    m.add("Excited about AI & ML", user_id=user_id, metadata={"category": "interests"})
    m.add("Likes to read books", user_id=user_id, metadata={"category": "interests"})

def populate_skills(linkedin_url: str, user_id: str):
    client = MultiOn(
        api_key=os.getenv("MULTION_API_KEY")
    )

    retrieveResponse = client.retrieve(
        cmd="Get perons's top skills from LinkedIn",
        url=linkedin_url,
        fields=["skill"],
        local=True

    )

    print(retrieveResponse)

    #remove duplicates
    skills = []
    for item in retrieveResponse.data:
        if item["skill"] not in skills:
            skills.append(item["skill"])

    for skill in skills:
        m.add(skill, user_id=user_id, metadata={"category": "skills"})



reset_memories("Bayram")

populate_memories("Bayram")
populate_skills("https://www.linkedin.com/in/bayramannakov/", "Bayram")


memories = m.get_all()

print(memories)