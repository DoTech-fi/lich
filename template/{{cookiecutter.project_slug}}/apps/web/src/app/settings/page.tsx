'use client';

import { useState } from 'react';
import Sidebar from '@/components/Layout/Sidebar/Sidebar';
import Header from '@/components/Layout/Header/Header';
import styles from '../dashboard/dashboard.module.css';
import formStyles from '../login/auth.module.css';

export default function SettingsPage() {
  const [theme, setTheme] = useState('dark');
  const [notifications, setNotifications] = useState(true);
  const [language, setLanguage] = useState('{{ cookiecutter.default_language }}');

  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        <Header />
        <div className={styles.content}>
          <h1>{% if cookiecutter.default_language == 'fa' %}تنظیمات{% else %}Settings{% endif %}</h1>
          
          <div className={styles.grid} style={% raw %}{{ marginTop: '2rem' }}{% endraw %}>
            <div className={styles.card}>
              <h3>{% if cookiecutter.default_language == 'fa' %}ظاهر{% else %}Appearance{% endif %}</h3>
              <div className={formStyles.field}>
                <label className={formStyles.label}>{% if cookiecutter.default_language == 'fa' %}تم{% else %}Theme{% endif %}</label>
                <select className={formStyles.input} value={theme} onChange={e => setTheme(e.target.value)}>
                  <option value="dark">🌙 Dark</option>
                  <option value="light">☀️ Light</option>
                </select>
              </div>
              <div className={formStyles.field}>
                <label className={formStyles.label}>{% if cookiecutter.default_language == 'fa' %}زبان{% else %}Language{% endif %}</label>
                <select className={formStyles.input} value={language} onChange={e => setLanguage(e.target.value)}>
                  <option value="fa">فارسی</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>

            <div className={styles.card}>
              <h3>{% if cookiecutter.default_language == 'fa' %}اعلان‌ها{% else %}Notifications{% endif %}</h3>
              <label className={formStyles.checkbox}>
                <input type="checkbox" checked={notifications} onChange={e => setNotifications(e.target.checked)} />
                <span>{% if cookiecutter.default_language == 'fa' %}فعال{% else %}Enabled{% endif %}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
