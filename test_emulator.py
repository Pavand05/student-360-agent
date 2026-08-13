import os
from google.cloud import firestore

print("FIRESTORE_EMULATOR_HOST:", os.environ.get("FIRESTORE_EMULATOR_HOST"))
db = firestore.Client(project="intern-bnmit-july-2026")
doc = db.collection("test").document("ping")
doc.set({"message": "Hello Firestore Emulator!", "status": "active"})
print("Document retrieved from emulator:", doc.get().to_dict())
