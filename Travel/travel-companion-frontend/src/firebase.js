// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAwqWTaZB9WHKj9D-gCrq6KUwV0xHug_1Y",
  authDomain: "travel-c840f.firebaseapp.com",
  projectId: "travel-c840f",
  storageBucket: "travel-c840f.appspot.com",
  messagingSenderId: "614865066212",
  appId: "1:614865066212:web:21025b5ea19bd24b0974f1",
  measurementId: "G-76E6VEE7PF"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };