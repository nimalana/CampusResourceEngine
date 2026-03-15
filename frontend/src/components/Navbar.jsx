import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/courses", label: "Courses" },
  { to: "/clubs", label: "Clubs" },
  { to: "/research", label: "Research" },
  { to: "/events", label: "Events" },
  { to: "/dining", label: "Dining" },
  { to: "/search", label: "Search" },
  { to: "/system", label: "System" },
];

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        UNC <span>Resource Engine</span>
      </NavLink>
      <div className="navbar-links">
        {LINKS.map(({ to, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
