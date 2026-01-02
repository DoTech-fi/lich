'use client';

/**
 * Header Component
 * Top navigation bar with user menu
 */

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import styles from './Header.module.css';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  return (
    <header className={styles.header}>
      <div className={styles.search}>
        <input 
          type="text" 
          placeholder="{% if cookiecutter.default_language == 'fa' %}جستجو...{% else %}Search...{% endif %}"
          className={styles.searchInput}
        />
      </div>

      <div className={styles.actions}>
        {/* Notifications */}
        <button className={styles.iconButton} aria-label="Notifications">
          🔔
        </button>

        {/* User Menu */}
        {isAuthenticated && user ? (
          <div className={styles.userMenu}>
            <button 
              className={styles.userButton}
              onClick={() => setShowMenu(!showMenu)}
            >
              <div className={styles.avatar}>
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt={user.full_name} />
                ) : (
                  <span>{user.full_name.charAt(0).toUpperCase()}</span>
                )}
              </div>
              <span className={styles.userName}>{user.full_name}</span>
              <span className={styles.chevron}>▼</span>
            </button>

            {showMenu && (
              <div className={styles.dropdown}>
                <Link href="/profile" className={styles.dropdownItem}>
                  👤 {% if cookiecutter.default_language == 'fa' %}پروفایل{% else %}Profile{% endif %}
                </Link>
                <Link href="/settings" className={styles.dropdownItem}>
                  ⚙️ {% if cookiecutter.default_language == 'fa' %}تنظیمات{% else %}Settings{% endif %}
                </Link>
                <hr className={styles.divider} />
                <button 
                  onClick={() => logout()}
                  className={styles.dropdownItem}
                >
                  🚪 {% if cookiecutter.default_language == 'fa' %}خروج{% else %}Logout{% endif %}
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link href="/login" className="btn btn-primary">
            {% if cookiecutter.default_language == 'fa' %}ورود{% else %}Login{% endif %}
          </Link>
        )}
      </div>
    </header>
  );
}
