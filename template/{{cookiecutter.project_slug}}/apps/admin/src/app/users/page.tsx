import Link from 'next/link';

export default function UsersPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Users Management</h1>
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600 mb-4">
          This page allows admins to manage users (change roles, suspend, etc.).
        </p>
        <div className="border rounded-md p-4 bg-gray-50">
          <p className="text-sm text-gray-500 italic">User list will be populated from the API here.</p>
        </div>
        <div className="mt-4">
            <Link href="/" className="text-blue-500 hover:underline">← Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
