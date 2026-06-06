import { initializeApp } from 'firebase/app'
import { getDatabase } from 'firebase/database'

const firebaseConfig = {
  apiKey: "AIzaSyCaA6QqEV746HjdSEAE7tESWBeiCv5GKkg",
  authDomain: "sentinel-edeb5.firebaseapp.com",
  databaseURL: "https://sentinel-edeb5-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "sentinel-edeb5",
  storageBucket: "sentinel-edeb5.firebasestorage.app",
  messagingSenderId: "958687125944",
  appId: "1:958687125944:web:011cabb9a1bbd365cf6f4d"
}

const app = initializeApp(firebaseConfig)
export const db = getDatabase(app)