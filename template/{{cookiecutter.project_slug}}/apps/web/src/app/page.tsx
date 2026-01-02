import styles from './page.module.css'

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.hero}>
        <h1 className={styles.title}>
          {% if cookiecutter.default_language == 'fa' %}به {% endif %}{{ cookiecutter.project_name }}{% if cookiecutter.default_language == 'fa' %} خوش آمدید{% endif %}
        </h1>
        <p className={styles.description}>
          {{ cookiecutter.project_description }}
        </p>
        <div className={styles.cta}>
          <a href="/dashboard" className="btn btn-primary">
            {% if cookiecutter.default_language == 'fa' %}ورود به داشبورد{% else %}Go to Dashboard{% endif %}
          </a>
          <a href="/api/docs" className="btn btn-secondary">
            {% if cookiecutter.default_language == 'fa' %}مستندات API{% else %}API Docs{% endif %}
          </a>
        </div>
      </div>
      
      <div className={styles.features}>
        <div className="card">
          <h3>🚀 {% if cookiecutter.default_language == 'fa' %}سریع و مدرن{% else %}Fast & Modern{% endif %}</h3>
          <p>{% if cookiecutter.default_language == 'fa' %}ساخته شده با Next.js 14 و FastAPI{% else %}Built with Next.js 14 and FastAPI{% endif %}</p>
        </div>
        <div className="card">
          <h3>🔐 {% if cookiecutter.default_language == 'fa' %}امن{% else %}Secure{% endif %}</h3>
          <p>{% if cookiecutter.default_language == 'fa' %}رعایت استانداردهای امنیتی OWASP{% else %}Following OWASP security standards{% endif %}</p>
        </div>
        <div className="card">
          <h3>📱 {% if cookiecutter.default_language == 'fa' %}واکنش‌گرا{% else %}Responsive{% endif %}</h3>
          <p>{% if cookiecutter.default_language == 'fa' %}طراحی مناسب برای همه دستگاه‌ها{% else %}Designed for all devices{% endif %}</p>
        </div>
      </div>
    </main>
  )
}
