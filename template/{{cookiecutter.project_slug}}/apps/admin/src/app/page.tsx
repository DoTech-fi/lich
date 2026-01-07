import Link from "next/link";
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <p>
          {{ cookiecutter.project_name }} Admin Panel
        </p>
      </div>

      <div className={styles.center}>
        <h1 className="text-4xl font-bold">Admin Dashboard</h1>
      </div>

      <div className={styles.grid}>
        <Link
          href="/users"
          className={styles.card}
        >
          <h2>
            Users <span>-&gt;</span>
          </h2>
          <p>Manage users, roles, and permissions.</p>
        </Link>
        
        <a
          href="http://localhost:3000"
          className={styles.card}
          target="_blank"
          rel="noopener noreferrer"
        >
          <h2>
            Main Site <span>-&gt;</span>
          </h2>
          <p>Go to the public website.</p>
        </a>
      </div>
    </main>
  );
}
