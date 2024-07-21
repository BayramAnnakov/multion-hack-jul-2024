import dotenv

dotenv.load_dotenv()

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


#m.add("I've heard from my colleague Tim about Lex Fridman's talk with Bill Ackman and his controversial political views and invesments ", user_id="Bayram", metadata={"category": "daily memories"})
# m.add("Likes to watch Lex Fridman's podcasts", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to build & participate in hackathons", user_id="Bayram", metadata={"category": "interests"})
# m.add("Excited about AI & ML", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to read books about systems thinking", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to read books about psychology", user_id="Bayram", metadata={"category": "interests"})
# m.add("Likes to read books about economics and investing", user_id="Bayram", metadata={"category": "interests"})

# memories = m.search(query="Bill Ackman talk with Lex Fridman", user_id="Bayram")

# print(memories)

memories = m.get_all()

print(memories)