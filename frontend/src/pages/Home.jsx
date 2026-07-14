import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";

function IconCluster() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle cx="6" cy="7" r="2.4" fill="currentColor" />
      <circle cx="6" cy="17" r="2.4" fill="currentColor" />
      <circle cx="16" cy="12" r="3.2" fill="currentColor" />
      <path d="M8 8.5 13.5 11M8 15.5 13.5 13" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

function IconGeo() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 21s-7-6.1-7-11.5A7 7 0 0 1 19 9.5C19 14.9 12 21 12 21Z"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <circle cx="12" cy="9.5" r="2.2" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

function IconStats() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M4 20V10M11 20V4M18 20v-7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
  );
}

export default function Home() {
  const { t } = useTranslation();

  return (
    <div className="page page-home">
      <div className="page-header">
        <div>
          <span className="page-eyebrow">{t("home_hero_badge")}</span>
          <h1>DengueSphere</h1>
          <p>{t("home_subtitle")}</p>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-tile">
          <span>{t("home_stat_algorithm_label")}</span>
          <strong>{t("home_stat_algorithm_value")}</strong>
        </div>
        <div className="stat-tile">
          <span>{t("home_stat_modules_label")}</span>
          <strong>{t("home_stat_modules_value")}</strong>
        </div>
        <div className="stat-tile">
          <span>{t("home_stat_geocoding_label")}</span>
          <strong>{t("home_stat_geocoding_value")}</strong>
        </div>
      </div>

      <div className="feature-grid">
        <div className="feature-card">
          <div className="feature-icon"><IconCluster /></div>
          <h3>{t("home_feature_cluster_title")}</h3>
          <p>{t("home_feature_cluster_desc")}</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon"><IconGeo /></div>
          <h3>{t("home_feature_geocode_title")}</h3>
          <p>{t("home_feature_geocode_desc")}</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon"><IconStats /></div>
          <h3>{t("home_feature_stats_title")}</h3>
          <p>{t("home_feature_stats_desc")}</p>
        </div>
      </div>

      <div className="readme-card">
        <h3>{t("home_welcome_header")}</h3>
        <div className="markdown-body">
          <ReactMarkdown>{t("home_main_text")}</ReactMarkdown>
        </div>
      </div>

      <div className="info-banner">{t("home_footer_info")}</div>
    </div>
  );
}
