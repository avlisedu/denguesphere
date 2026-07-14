import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

function IconHome() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M4 11.5 12 5l8 6.5V19a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconPin() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 21s-7-6.1-7-11.5A7 7 0 0 1 19 9.5C19 14.9 12 21 12 21Z"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <circle cx="12" cy="9.5" r="2.2" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

function IconCluster() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <circle cx="6" cy="7" r="2.1" fill="currentColor" />
      <circle cx="6" cy="17" r="2.1" fill="currentColor" />
      <circle cx="16" cy="12" r="2.9" fill="currentColor" />
      <path d="M8 8.3 13.5 11M8 15.7 13.5 13" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

function IconInfo() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="8.3" stroke="currentColor" strokeWidth="1.7" />
      <path d="M12 11v5.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="8" r="1" fill="currentColor" />
    </svg>
  );
}

const LINKS = [
  { to: "/", end: true, key: "nav_home", Icon: IconHome },
  { to: "/coordenadas", key: "nav_coords", Icon: IconPin },
  { to: "/clusterizador", key: "nav_cluster", Icon: IconCluster },
  { to: "/sobre", key: "nav_about", Icon: IconInfo },
];

export default function Sidebar() {
  const { t, i18n } = useTranslation();

  return (
    <aside className="sidebar">
      <NavLink to="/" className="brand" end>
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="34" height="34">
            <circle cx="16" cy="16" r="3.2" fill="#0e6b52" />
            <ellipse cx="16" cy="16" rx="12.5" ry="5.2" fill="none" stroke="#0e6b52" strokeWidth="1.6" />
            <ellipse cx="16" cy="16" rx="12.5" ry="5.2" fill="none" stroke="#4fae8c" strokeWidth="1.6" transform="rotate(60 16 16)" />
            <ellipse cx="16" cy="16" rx="12.5" ry="5.2" fill="none" stroke="#89cbb0" strokeWidth="1.6" transform="rotate(120 16 16)" />
          </svg>
        </span>
        <span className="brand-name">
          Dengue<span className="brand-accent">Sphere</span>
        </span>
      </NavLink>

      <nav className="sidebar-nav">
        {LINKS.map(({ to, end, key, Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
          >
            <Icon />
            {t(key)}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="lang-switch" role="group" aria-label={t("lang_label")}>
          <button
            type="button"
            className={i18n.language === "pt" ? "active" : ""}
            onClick={() => i18n.changeLanguage("pt")}
          >
            PT
          </button>
          <button
            type="button"
            className={i18n.language === "en" ? "active" : ""}
            onClick={() => i18n.changeLanguage("en")}
          >
            EN
          </button>
        </div>
        <small>DengueSphere · GPSID / PPGEP-UFPE</small>
      </div>
    </aside>
  );
}
