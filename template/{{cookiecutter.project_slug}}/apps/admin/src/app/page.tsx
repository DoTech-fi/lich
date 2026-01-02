import styles from './page.module.css'

export default function AdminHome() {
  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <h1>{{ cookiecutter.project_name }} Admin</h1>
        <p>Administration Dashboard</p>
      </div>
      
      <div className={styles.grid}>
        <a href="/users" className={styles.card}>
          <h2>👥 Users</h2>
          <p>Manage user accounts</p>
        </a>
        
        <a href="/settings" className={styles.card}>
          <h2>⚙️ Settings</h2>
          <p>System configuration</p>
        </a>
        
        <a href="/logs" className={styles.card}>
          <h2>📋 Logs</h2>
          <p>View system logs</p>
        </a>
        
        <a href="/analytics" className={styles.card}>
          <h2>📊 Analytics</h2>
          <p>Usage statistics</p>
        </a>
      </div>
    </main>
  )
}
