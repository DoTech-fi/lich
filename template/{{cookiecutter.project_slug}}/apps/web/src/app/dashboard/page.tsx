'use client';

/**
 * Dashboard Page
 * Main dashboard after login
 */

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Layout/Sidebar/Sidebar';
import Header from '@/components/Layout/Header/Header';
import styles from './dashboard.module.css';

interface StatCardProps {
  icon: string;
  label: string;
  value: string;
  change?: string;
  positive?: boolean;
}

function StatCard({ icon, label, value, change, positive }: StatCardProps) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statIcon}>{icon}</div>
      <div className={styles.statContent}>
        <p className={styles.statLabel}>{label}</p>
        <p className={styles.statValue}>{value}</p>
        {change && (
          <p className={`${styles.statChange} ${positive ? styles.positive : styles.negative}`}>
            {positive ? '↑' : '↓'} {change}
          </p>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user, isLoading, isAuthenticated } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}>⏳</div>
        <p>{% if cookiecutter.default_language == 'fa' %}در حال بارگذاری...{% else %}Loading...{% endif %}</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return null;
  }

  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        <Header />
        <div className={styles.content}>
          <div className={styles.welcome}>
            <h1>
              {% if cookiecutter.default_language == 'fa' %}
              سلام {user?.first_name || user?.username} 👋
              {% else %}
              Hello, {user?.first_name || user?.username} 👋
              {% endif %}
            </h1>
            <p>
              {% if cookiecutter.default_language == 'fa' %}
              به داشبورد خوش آمدید
              {% else %}
              Welcome to your dashboard
              {% endif %}
            </p>
          </div>

          <div className={styles.stats}>
            <StatCard
              icon="📊"
              label="{% if cookiecutter.default_language == 'fa' %}کل فروش{% else %}Total Sales{% endif %}"
              value="$12,345"
              change="12%"
              positive={true}
            />
            <StatCard
              icon="👥"
              label="{% if cookiecutter.default_language == 'fa' %}کاربران{% else %}Users{% endif %}"
              value="1,234"
              change="5%"
              positive={true}
            />
            <StatCard
              icon="📈"
              label="{% if cookiecutter.default_language == 'fa' %}بازدید{% else %}Visits{% endif %}"
              value="56,789"
              change="3%"
              positive={false}
            />
            <StatCard
              icon="⭐"
              label="{% if cookiecutter.default_language == 'fa' %}امتیاز{% else %}Rating{% endif %}"
              value="4.8"
            />
          </div>

          <div className={styles.grid}>
            <div className={styles.card}>
              <h3>{% if cookiecutter.default_language == 'fa' %}فعالیت اخیر{% else %}Recent Activity{% endif %}</h3>
              <ul className={styles.activityList}>
                <li className={styles.activityItem}>
                  <span className={styles.activityIcon}>🔔</span>
                  <div>
                    <p>{% if cookiecutter.default_language == 'fa' %}ورود جدید{% else %}New login{% endif %}</p>
                    <small>{% if cookiecutter.default_language == 'fa' %}۲ دقیقه پیش{% else %}2 minutes ago{% endif %}</small>
                  </div>
                </li>
                <li className={styles.activityItem}>
                  <span className={styles.activityIcon}>✅</span>
                  <div>
                    <p>{% if cookiecutter.default_language == 'fa' %}پروفایل به‌روز شد{% else %}Profile updated{% endif %}</p>
                    <small>{% if cookiecutter.default_language == 'fa' %}۱ ساعت پیش{% else %}1 hour ago{% endif %}</small>
                  </div>
                </li>
                <li className={styles.activityItem}>
                  <span className={styles.activityIcon}>📧</span>
                  <div>
                    <p>{% if cookiecutter.default_language == 'fa' %}ایمیل تأیید شد{% else %}Email verified{% endif %}</p>
                    <small>{% if cookiecutter.default_language == 'fa' %}دیروز{% else %}Yesterday{% endif %}</small>
                  </div>
                </li>
              </ul>
            </div>

            <div className={styles.card}>
              <h3>{% if cookiecutter.default_language == 'fa' %}کارهای امروز{% else %}Quick Actions{% endif %}</h3>
              <div className={styles.actions}>
                <a href="/profile" className={styles.actionButton}>
                  👤 {% if cookiecutter.default_language == 'fa' %}ویرایش پروفایل{% else %}Edit Profile{% endif %}
                </a>
                <a href="/settings" className={styles.actionButton}>
                  ⚙️ {% if cookiecutter.default_language == 'fa' %}تنظیمات{% else %}Settings{% endif %}
                </a>
                <a href="/help" className={styles.actionButton}>
                  ❓ {% if cookiecutter.default_language == 'fa' %}راهنما{% else %}Help{% endif %}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
