import { initializeApp } from "firebase/app";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";

// Firebase web configuration (uses GCP project intern-bnmit-july-2026)
const firebaseConfig = {
  projectId: "intern-bnmit-july-2026",
  appId: "student-360-agent-app",
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Connect to local Firestore Emulator if running on localhost or dev mode
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
if (isLocalhost) {
  try {
    connectFirestoreEmulator(db, "127.0.0.1", 8080);
    console.log("[Firebase] Connected to local Firestore Emulator on port 8080");
  } catch (err) {
    console.warn("[Firebase] Emulator connection notice:", err);
  }
}

export { db };
