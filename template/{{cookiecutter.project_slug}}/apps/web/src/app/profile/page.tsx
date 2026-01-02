'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { usersApi } from '@/lib/api-client';
import Sidebar from '@/components/Layout/Sidebar/Sidebar';
import Header from '@/components/Layout/Header/Header';
import styles from '../dashboard/dashboard.module.css';
import formStyles from '../login/auth.module.css';

export default function ProfilePage() {
  const { user, refreshUser, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await usersApi.updateMe({
        first_name: formData.firstName,
        last_name: formData.lastName,
      });
      await refreshUser();
      setMessage('✅ {% if cookiecutter.default_language == "fa" %}ذخیره شد{% else %}Saved{% endif %}');
    } catch {
      setMessage('❌ {% if cookiecutter.default_language == "fa" %}خطا{% else %}Error{% endif %}');
    }
    setIsSaving(false);
  };

  if (isLoading) return <div className={styles.loading}>⏳</div>;

  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        <Header />
        <div className={styles.content}>
          <h1>{% if cookiecutter.default_language == 'fa' %}پروفایل{% else %}Profile{% endif %}</h1>
          <div className={styles.card} style={% raw %}{{ marginTop: '2rem', maxWidth: 500 }}{% endraw %}>
            {message && <p style={% raw %}{{ marginBottom: '1rem' }}{% endraw %}>{message}</p>}
            <form onSubmit={handleSubmit} className={formStyles.form}>
              <div className={formStyles.field}>
                <label className={formStyles.label}>{% if cookiecutter.default_language == 'fa' %}نام{% else %}First Name{% endif %}</label>
                <input className={formStyles.input} value={formData.firstName} 
                  onChange={e => setFormData({...formData, firstName: e.target.value})} />
              </div>
              <div className={formStyles.field}>
                <label className={formStyles.label}>{% if cookiecutter.default_language == 'fa' %}نام خانوادگی{% else %}Last Name{% endif %}</label>
                <input className={formStyles.input} value={formData.lastName}
                  onChange={e => setFormData({...formData, lastName: e.target.value})} />
              </div>
              <button type="submit" className={formStyles.button} disabled={isSaving}>
                {isSaving ? '⏳' : '{% if cookiecutter.default_language == "fa" %}ذخیره{% else %}Save{% endif %}'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
