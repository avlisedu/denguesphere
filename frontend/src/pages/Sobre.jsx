import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";

export default function Sobre() {
  const { t } = useTranslation();

  return (
    <div className="page page-sobre">
      <h1>{t("about_title")}</h1>

      <div className="info-box markdown-body">
        <ReactMarkdown>{t("about_infobox")}</ReactMarkdown>
      </div>

      <div className="sobre-grid">
        <div className="sobre-card">
          <h2>{t("about_team_header")}</h2>
          <div className="markdown-body">
            <ReactMarkdown>{t("about_team_list")}</ReactMarkdown>
          </div>
        </div>

        <div className="sobre-card">
          <h2>{t("about_objectives_header")}</h2>
          <div className="markdown-body">
            <ReactMarkdown>{t("about_objectives_list")}</ReactMarkdown>
          </div>
        </div>
      </div>

      <div
        className="footer-box"
        dangerouslySetInnerHTML={{ __html: t("about_footer") }}
      />
    </div>
  );
}
