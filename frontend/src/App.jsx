import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Courses from "./pages/Courses";
import Clubs from "./pages/Clubs";
import Research from "./pages/Research";
import Events from "./pages/Events";
import Dining from "./pages/Dining";
import Search from "./pages/Search";
import SystemDashboard from "./pages/SystemDashboard";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="page-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/clubs" element={<Clubs />} />
          <Route path="/research" element={<Research />} />
          <Route path="/events" element={<Events />} />
          <Route path="/dining" element={<Dining />} />
          <Route path="/search" element={<Search />} />
          <Route path="/system" element={<SystemDashboard />} />
        </Routes>
      </main>
    </div>
  );
}
