import Link from "next/link";

export default function Header() {
  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-blue-600">
          PDF to Excel
        </Link>
        <nav className="flex gap-6">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            Home
          </Link>
          <Link href="/tool/pdf-to-excel" className="text-gray-600 hover:text-gray-900">
            Tool
          </Link>
          <Link href="/about" className="text-gray-600 hover:text-gray-900">
            About
          </Link>
        </nav>
      </div>
    </header>
  );
}
