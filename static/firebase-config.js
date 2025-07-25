import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-database.js";


//for local
const firebaseConfig = {
    apiKey: "AIzaSyA9tk6lfzSOb_cj_6hXmBmm4Oa2W2kUhRw",
    authDomain: "attendancesystem-4c6f4.firebaseapp.com",
    databaseURL: "https://attendancesystem-4c6f4-default-rtdb.firebaseio.com",
    projectId: "attendancesystem-4c6f4",
    storageBucket: "attendancesystem-4c6f4.firebasestorage.app",
    messagingSenderId: "592854285285",
    appId: "1:592854285285:web:030d3bdf07e585c7b8cd0c",
    measurementId: "G-LJYXHDX3BB"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const database = getDatabase(app);

export { auth, database };
