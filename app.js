/*async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://127.0.0.1:8000/login", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        email,
        password
    })
});

    const data = await response.json();
    console.log(data);
}*/

import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import AdminDashboard from "./pages/AdminDashboard";
import MemberDashboard from "./pages/MemberDashboard";

function App() {
    return (
        <BrowserRouter>
            <Routes>

                {/* Login Page */}
                <Route path="/" element={<Login />} />

                {/* Admin Dashboard */}
                <Route
                    path="/admin-dashboard"
                    element={<AdminDashboard />}
                />

                {/* Member Dashboard */}
                <Route
                    path="/member-dashboard"
                    element={<MemberDashboard />}
                />

            </Routes>
        </BrowserRouter>
    );
}

export default App;

